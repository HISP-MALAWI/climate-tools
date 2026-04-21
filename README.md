# Climate Tools

**Climate Tools** is the umbrella project for working with DHIS2 and environmental / climate-related data.  
It includes online documentation, guides, tutorials, and the `dhis2eo` Python package and CLI tool.

- For a quick introduction to the project, see the [Introduction page](docs/intro.md).
- To install `dhis2eo` package for Python and CLI, see the [Installation page](docs/getting-started/installation.md).
- For documentation on how to use `dhis2eo` and other workflows, see https://dhis2.github.io/climate-tools.
- To get started as a contributor, see the [How to Contribute page](docs/contribute.md).

## DHIS2 credentials

Scripts that fetch data from DHIS2 (e.g. `dhis2eo/gridding/redistribution.py`) read the password from a `.env` file. Create `dhis2eo/gridding/.env` with:

```
DHIS2_PASSWORD=your-password-here
```

The `.env` file is git-ignored. Do not commit credentials.
