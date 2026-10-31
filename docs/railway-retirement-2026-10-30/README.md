# Railway retirement configuration backup

Project: `dspy-reference-example`. Captured 2026-10-30 (America/Chicago).

The recovery files contain the exported Railway resource graph, build/deploy/networking settings, service variable values and references, original status metadata, and function source where present. They are encrypted with age to the owner's existing SSH Ed25519 public key. Each file was decrypted locally and compared byte for byte before publication. `manifest.json` lists ciphertext checksums.

These are configuration backups. Database rows, volume filesystem contents, and bucket objects are not included. Source and tracked build configuration remain on the repository's original branches. No application source was changed for this backup.

Decrypt an individual file locally with `age --decrypt --identity ~/.ssh/id_ed25519 ENVIRONMENT.recovery.json.age > recovery.json`. Keep the output private; it contains credentials. Sealed variables, if any, cannot be recovered from the API.

Services were stopped before archival. The AcmeTools starter function's hourly schedule was removed. TestCompare was preserved separately. Check Railway for the current project deletion/recovery state.
