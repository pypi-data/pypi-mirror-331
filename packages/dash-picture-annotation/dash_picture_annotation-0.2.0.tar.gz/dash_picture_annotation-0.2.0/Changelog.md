# Dash Picture Annotation

{:toc}

## CHANGELOG

### 0.2.0 @ 03/03/2025

#### :mega: New

1. Improve and add the scaling control features. Now, the annotated image scale behaves more like the `<img>` tag. Users can use a new property, `init_scale`, to fine-grain control the scale.
2. Add utilities and typehints related to the newly introduced `scale` features. It is recommended that `dpa.sanitize_scale` can be used to create `dpa.Scale`.
3. Add demo of the new feature `init_scale` to `usage.py`.

#### :floppy_disk: Change

1. Bump the `yarn` version from `4.5.3` to `4.7.0`.
2. Add the dependency `react-image-size`.

### 0.1.2 @ 12/01/2024

#### :wrench: Fix

1. Fix: Correct typos in the docstrings.
2. Fix: Add `examples/*` to the include list of `MANIFEST.in`.
3. Fix: The `examples/*` should be included in the Dockerfile. The configurations related to it has been corrected.

#### :floppy_disk: Change

1. Bump the `yarn` version from `4.5.1` to `4.5.3`.

### 0.1.1 @ 11/10/2024

#### :floppy_disk: Change

1. Add the missing document information to the package metadata.

### 0.1.0 @ 11/10/2024

#### :mega: New

1. Add the security policy file.

#### :wrench: Fix

1. Fix: Lossen the input argument type of `sanitize_data(...)` and `sanitize_data_item(...)`. Previously, passing not sanitized data to these functions will cause type checking issues.
2. Fix: Fix a severe bug of importing the components in a wrong list. Now the scope is limited to the auto-generated codes.

#### :floppy_disk: Change

1. Change the configuration of the paths in the `usage.py`.

### 0.1.0 @ 11/06/2024

#### :mega: New

1. Add typehints: `AnnoStyle`, `DashSelectOptionItem`, and `Size`.

#### :wrench: Fix

1. Fix: Fix few typos in the docstrings.
2. Fix: Fix the aliases in the top-level package.

#### :floppy_disk: Change

1. Upgrade Yarn to `v4.5.1`.
2. Downgrade React to `v18.2.x` because the `defaultProps` which is used by Dash is marked as deprecated since `v18.3.0`.

### 0.1.0 @ 11/04/2024

#### :mega: New

1. Create this project.
2. Finish the react implement `src` and the automatically generated package `dash_picture_annotation`.
3. Add the React demo `App.js`.
4. Add the Dash demo `usage.py` and more examples in `./examples`.
5. Add the unit tests in `./tests`.
6. Add configurations `pyproject.toml`.
7. Add the devloper's environment folder `./docker` and the `Dockerfile`.
8. Add GitHub workflows and issue/PR templates.
9. Add the banner in the readme file.

#### :wrench: Fix

1. Fix: Fix the video link in the readme file.
