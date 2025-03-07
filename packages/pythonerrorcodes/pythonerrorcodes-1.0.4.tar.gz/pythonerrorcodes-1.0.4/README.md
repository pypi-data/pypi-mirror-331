# central-error-codes

## Setup Instructions

### Prerequisites
- Ensure you have **Node.js** and **Python 3** installed on your system.
- Install **npm** and **pip** for managing dependencies.

### Installation

#### Clone the Repository
```sh
 git clone <repo-url>
 cd central-error-codes
```

#### Setup Node.js Module
```sh
cd src/typescript
npm install
npm run build
```

#### Setup Python Module
```sh
cd src/python
pip install -r requirements.txt
python3 setup.py install
```

### Usage

#### Using Node.js Module in Another Project
```sh
npm install /path/to/central-error-codes
```
Import in your project:
```javascript
import ErrorCode from 'central-error-codes';
ErrorCode.getGenericError();
```

#### Using Python Module in Another Project
```sh
pip install /path/to/central-error-codes/dist/python_package.tar.gz
```
Import in your Python script:
```python
from cagent_errorcode import ErrorCode
ErrorCode.get_generic_error()
```

### Building Both Modules in One Command
```sh
npm run build
```
Ensure that `package.json` has:
```json
"scripts": {
  "build": "npm run build && python3 setup.py sdist"
}
```

### Troubleshooting
- If you face `ModuleNotFoundError: No module named 'setuptools'`, install it using:
  ```sh
  pip install setuptools
  ```
- If `tsc` is not found, install TypeScript globally:
  ```sh
  npm install -g typescript
  ```

For any issues, feel free to raise a GitHub issue in the repository!

