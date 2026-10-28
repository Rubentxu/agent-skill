// Ejemplo sintético: ninguna dependencia externa ni aplicación real.
// El contrato de errores aún NO se ha caracterizado.
pub trait SearchPort {
    fn search(&self, query: &str) -> Result<usize, String>;
}
pub trait MetricsPort {
    fn record(&self, found: usize) -> Result<(), String>;
}

pub struct SearchUseCase<S, M> {
    pub search: S,
    pub metrics: M,
}

impl<S: SearchPort, M: MetricsPort> SearchUseCase<S, M> {
    pub fn execute(&self, query: &str) -> Result<usize, String> {
        if query.trim().is_empty() {
            return Err("empty query".to_string());
        }
        let count = self.search.search(query)?;
        self.metrics.record(count)?;
        Ok(count)
    }
}
