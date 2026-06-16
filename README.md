# sonic-formal-infra

> Formal methods infrastructure for SONiC.

## Overview

Routing software maintains deep, nested data structures and implements
entangled protocol features. Such software is hard to test thoroughly by hand.
Instead, we write an *executable model as the spec* for a piece of behavior,
auto-generate high-coverage test cases from it (symbolic execution), and
replay them against the real C implementation to check conformance.

A model captures the **State**, **Transition**, and **Precondition**.
See [`examples/bgpd_nexthop_mgmt`](examples/bgpd_nexthop_mgmt/README.md) for an example (FRR `bgpd` nexthop tracking).

This project provides a common library to facilitate writing formal models
and systematically generating tests for SONiC components.
In addition, it hosts formal models of various modules and network features
within the SONiC ecosystem.

## Repository layout

Run everything from the repo root: it is the single import root, so a model's
`from mbt... import ...` resolves with no `PYTHONPATH` tricks.

```
sonic-formal-infra/
├── mbt/                        # shared library — the one common package models import
│   └── prims.py                #   model-writing primitives (types, render, predicates, collections)
├── models/                     # real, focused models — one slice of behavior each
│   └── <module>/<feature>/     #   module dir is a namespace (e.g. bgpd/nexthop_mgmt)
│       ├── model.py            #     State / Transition / Precondition
│       ├── generated/          #     committed test-cases
│       └── test_driver/        #     C++ harness to drive the real implementation
├── examples/                   # demos — e.g. bgpd_nexthop_mgmt (has its own README)
├── LICENSE                     # Apache-2.0
└── README.md
```

- `mbt/` holds the model-writing primitives. It may include utility code for test
  generation and execution in the future.
- `models/` is where real models live, one `<module>/<feature>` slice each — empty
  for now.

Planned: `interactions/` for P models composing interacting models into call sequences.

## Contributing

- **Add a new model** — define the State / Transition / Precondition, and generate
  test cases.
- **Share a bug** — found a real implementation bug using this infra? We want
  to collect these. (submission process TBD)

This repo follows the SONiC project's
[contribution conventions](https://github.com/sonic-net/SONiC/blob/master/CONTRIBUTING.md):

- **Pull requests** — use GitHub Flow; keep each commit scoped to a single
  component/fix/feature, with tests and docs (maintainers do the merge).
- **Commit messages** — follow SONiC's format, including the `Signed-off-by` line
  (`git commit -s`):

  ```
  [component/folder touched]: Description intent of your changes

  [List of changes]

  Signed-off-by: Your Name <your@email.com>
  ```

- **CLA** — sign the Individual Contributor License Agreement (ICLA) before a PR
  can be merged. You will be prompted once the PR is created.

## Community

Developed by the [SONiC Formal Methods Working Group](https://lists.sonicfoundation.dev/g/sonic-formal-methods-wg).

## License

Licensed under the Apache License 2.0 — see [LICENSE](LICENSE).
