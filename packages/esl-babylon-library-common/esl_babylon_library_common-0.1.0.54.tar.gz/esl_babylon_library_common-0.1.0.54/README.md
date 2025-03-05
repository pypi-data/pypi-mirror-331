# ESL Babylon Library Common

The **ESL Babylon Library Common** is a Python library that provides essential components and utilities. To integrate 
this library into your project, you'll need to configure your environment and dependency management system correctly.

---

## Installation Instructions

Follow these steps to use the `epam_gitlab` package repository:

### 1. Add the EPAM GitLab Package Source
Run the following command to add the package source to your Poetry configuration:

```bash
poetry source add epam_gitlab https://git.epam.com/api/v4/projects/304542/packages/pypi/simple --priority supplemental
```

### 2. Configure Authentication
Set up authentication for the `epam_gitlab` package repository by replacing `<access_token>` with your personal EPAM 
access token:

```bash
poetry config http-basic.epam_gitlab __token__ <access_token>
```

> **Example:**  
> If your access token is `kYsyto72PffB2Zjj5Uz9`, the command will look like this:  
> ```bash
> poetry config http-basic.epam_gitlab __token__ kYsyto72PffB2Zjj5Uz9
> ```

### 3. Add the Package to Your Project
Run the following command to include the library in your project dependencies. Replace `<package_name>` with the 
appropriate package name.

```bash
poetry add <package_name> --source epam_gitlab
```

> **Example:**  
> To install `esl-babylon-library-common`, execute:  
> ```bash
> poetry add esl-babylon-library-common --source epam_gitlab
> ```

---

## Environment Configuration

To use this library successfully, ensure your environment is properly configured.

### `.env` File Requirements
In the directory where your code is executed (or in any higher-level directory in the folder tree), there must be a 
`.env` file containing the required configuration.

#### Example
You can reference the structure and contents of a valid `.env` file in the provided `.env.example` file.

### Alternative Location
Alternatively, the `.env` file can be located in the `babylon` directory under the following path:

```
babylon/BUILD/.env
```

Ensure this file contains all necessary environment variables for the library to function properly.

---

## Notes

- Make sure your `.env` file or `babylon/BUILD/.env` file is properly set up before running your project to avoid 
runtime errors.
- Always keep your tokens and sensitive information secure.

---

Now you're all set to use the **ESL Babylon Library Common** in your project! 🎉

