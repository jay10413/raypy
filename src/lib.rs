use pyo3::prelude::*;
use rayon::prelude::*;

/// Runs a Python function in parallel across CPU cores using Rayon.
/// 
/// # Arguments
/// * `py_func` - A Python callable object
/// * `inputs` - A vector of integers to process
/// * `py` - The Python interpreter instance
///
/// # Returns
/// A vector of integers (results from applying py_func to each input)
#[pyfunction]
fn run_parallel(
    py_func: PyObject,
    inputs: Vec<i32>,
    py: Python,
) -> PyResult<Vec<i32>> {
    // Release the GIL and run Rayon parallel iterator
    let results = py.allow_threads(|| {
        inputs
            .par_iter()
            .map(|&input| {
                // Re-acquire GIL for each thread to call Python function
                Python::with_gil(|py| {
                    let py_input = input.into_py(py);
                    match py_func.call1(py, (py_input,)) {
                        Ok(result) => {
                            // Extract i32 from Python result
                            match result.extract::<i32>(py) {
                                Ok(value) => value,
                                Err(_) => {
                                    eprintln!("Warning: Could not extract i32 from result");
                                    0
                                }
                            }
                        }
                        Err(e) => {
                            eprintln!("Error calling Python function: {}", e);
                            0
                        }
                    }
                })
            })
            .collect()
    });

    Ok(results)
}

/// PyO3 module definition for raypy
#[pymodule]
fn raypy(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_parallel, m)?)?;
    Ok(())
}
