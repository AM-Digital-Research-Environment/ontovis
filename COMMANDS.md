# `ontovis`

Visualize and analyze WissKI pathbuilder definitions

**Usage**:

```console
$ ontovis [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `render`: Render a graphical representation of a...
* `stats`: Foo.

## `ontovis render`

Render a graphical representation of a pathbuilder definition.

Use `--template` to select a builtin template, or use `--template-custom` to
pass your own template.


The builtin templates are:

* no_groups (default): render only the ontology-classes and omit grouping
  into fields and path-groups.

* no_fields: group the ontology classes into path-groups, omit fields.

* full: group classes into fields, and fields into path-groups. **Warning:**
  the resulting representation can become very dense.

To pass a custom template using `--template-custom`, use
[jinja2](https://jinja.palletsprojects.com/en/stable/templates/)
to author a template.

Your template will have to work with the parser&#x27;s intermediate
representation; pass the `--raw` flag to see this.

**Usage**:

```console
$ ontovis render [OPTIONS] INPUT
```

**Arguments**:

* `INPUT`: [required]

**Options**:

* `--template [no_groups|no_fields|full]`: [default: no_groups]
* `--template-custom PATH`
* `--skip-disabled / --include-disabled`: [default: skip-disabled]
* `-r, --raw`
* `--help`: Show this message and exit.

## `ontovis stats`

Foo.

**Usage**:

```console
$ ontovis stats [OPTIONS] INPUT
```

**Arguments**:

* `INPUT`: [required]

**Options**:

* `--help`: Show this message and exit.

