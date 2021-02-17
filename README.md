# advmlthreatmatrix data

Data for adversarial ml threat matrix.

The advmlthreatmatrix data is stored in yaml files designed to be easy to read and edit, but also easy to load, parse, and validate.

`matrix.yaml` contains the metadata for the matrix and references the underlying data files for tactics and techniques. It also allows for referencing external threat intelligence such as ATT&CK.

`tactics.yaml` contains all of the adversarial ML tactics.

`techniques.yaml` contains all of the adversarial ML techniques.

`schema.yaml` defines the schemai for the matrix, and technique and tactic objects.

### data validation

validate data by running the linter and validating against the advml schema after making changes.

```
yamllint *.yaml
```

```
yamale matrix.yaml
yamale tactics.yaml
yamale techniques.yaml
```
