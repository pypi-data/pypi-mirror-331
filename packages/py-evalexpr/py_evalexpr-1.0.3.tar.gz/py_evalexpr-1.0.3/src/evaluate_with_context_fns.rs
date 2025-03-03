use crate::error_mapping::convert_evalexpr_error;
use evalexpr::{
    eval_boolean_with_context, eval_empty_with_context, eval_float_with_context, eval_int_with_context, eval_number_with_context, eval_string_with_context,
    eval_tuple_with_context, eval_with_context, EvalexprResult, TupleType, Value,
};
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::{pyfunction, pymodule, Bound, PyObject, PyResult, Python};
use std::ops::Deref;

#[pymodule]
pub mod evaluate_with_context {
    use super::*;
    use crate::remap::convert_to_py_tuple;

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        Python::with_gil(|py| {
            let mod_name = "py_evalexpr.natives.evaluate_with_context";
            py.import("sys")?.getattr("modules")?.set_item(mod_name, m)?;
            // There's a bug with pyo3 that makes the __module__ attribute of functions on submodules incorrect, so we have to iterate over the functions and set the __module__ attribute manually.
            let all = m.getattr("__all__")?.extract::<Vec<String>>()?;
            for name in all {
                let func = m.getattr(&name)?;
                func.setattr("__module__", mod_name)?;
            }
            Ok(())
        })
    }

    #[pyfunction]
    fn evaluate_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<PyObject> {
        let result: EvalexprResult<Value> = eval_with_context(expression, context.deref());

        Python::with_gil(|py| match result {
            Ok(value) => Ok(crate::remap::convert_to_eval_result(py, value)?),
            Err(e) => Err(convert_evalexpr_error(&e)),
        })
    }

    #[pyfunction]
    fn evaluate_string_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<String> {
        let result: EvalexprResult<String> = eval_string_with_context(expression, context.deref());

        match result {
            Ok(value) => Ok(value),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }

    #[pyfunction]
    fn evaluate_int_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<i64> {
        let result: EvalexprResult<i64> = eval_int_with_context(expression, context.deref());

        match result {
            Ok(value) => Ok(value),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }

    #[pyfunction]
    fn evaluate_float_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<f64> {
        let result: EvalexprResult<f64> = eval_float_with_context(expression, context.deref());

        match result {
            Ok(value) => Ok(value),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }

    #[pyfunction]
    fn evaluate_number_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<f64> {
        let result: EvalexprResult<f64> = eval_number_with_context(expression, context.deref());

        match result {
            Ok(value) => Ok(value),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }

    #[pyfunction]
    fn evaluate_boolean_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<bool> {
        let result: EvalexprResult<bool> = eval_boolean_with_context(expression, context.deref());

        match result {
            Ok(value) => Ok(value),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }

    #[pyfunction]
    fn evaluate_tuple_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<PyObject> {
        let result: EvalexprResult<TupleType> = eval_tuple_with_context(expression, context.deref());

        Python::with_gil(|py| match result {
            Ok(value) => Ok(convert_to_py_tuple(py, value)),
            Err(e) => Err(convert_evalexpr_error(&e)),
        })?
    }

    #[pyfunction]
    fn evaluate_empty_with_context(expression: &str, context: &crate::context::context::EvalContext) -> PyResult<()> {
        let result: EvalexprResult<()> = eval_empty_with_context(expression, context.deref());

        match result {
            Ok(_) => Ok(()),
            Err(e) => Err(convert_evalexpr_error(&e)),
        }
    }
}
