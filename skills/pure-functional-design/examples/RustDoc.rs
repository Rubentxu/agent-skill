// Ejemplo sin bibliotecas externas: modelado de un workflow y decisión pura.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DocState {
    Draft { id: String },
    Published { id: String, version: u64 },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Command { Publish { version: u64 } }

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DomainError { InvalidVersion, AlreadyPublished }

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DomainEvent { Published { id: String, version: u64 } }

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Decision { pub next: DocState, pub events: Vec<DomainEvent> }

pub fn decide(state: &DocState, command: Command) -> Result<Decision, DomainError> {
    match (state, command) {
        (_, Command::Publish { version: 0 }) => Err(DomainError::InvalidVersion),
        (DocState::Draft { id }, Command::Publish { version }) => Ok(Decision {
            next: DocState::Published { id: id.clone(), version },
            events: vec![DomainEvent::Published { id: id.clone(), version }],
        }),
        (DocState::Published { .. }, Command::Publish { .. }) => Err(DomainError::AlreadyPublished),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn publish_draft_is_pure_and_emits_one_event() {
        let original = DocState::Draft { id: "doc-1".into() };
        let output = decide(&original, Command::Publish { version: 1 }).unwrap();
        assert_eq!(original, DocState::Draft { id: "doc-1".into() });
        assert_eq!(output.next, DocState::Published { id: "doc-1".into(), version: 1 });
        assert_eq!(output.events.len(), 1);
    }
}
