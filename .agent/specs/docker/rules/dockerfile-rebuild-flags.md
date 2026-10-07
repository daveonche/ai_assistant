# Rule: Rebuild flags

These flags are commonly confused: `--pull` refreshes the base image,
`--no-cache` re-executes build steps. Combine them for a fresh base image
plus re-run steps.

| Flag | Effect |
| :--- | :--- |
| `--pull` | Forces a check for and download of a newer base image, even if one is cached locally. |
| `--no-cache` | Disables the build cache and re-fetches dependency versions from package managers; does not refresh the base image. |

```bash
docker build --pull --no-cache -t my-image:my-tag .
```
