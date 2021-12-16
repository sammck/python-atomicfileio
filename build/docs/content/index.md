# iotlib
Python package for atomically updating files.


## Dev setup

To set up a development environment, 

```bash
cd $HOME
git clone git@github.com:sammck/python-atomicfileio.git
cd python-atomicfileio
# set environment variables as described above
./init-env.sh
```

After successful initialization, the relevant env vars will be persisted into a gitignore'd file
`.dev-env`.  After that, you should no longer need to set those environment variables directly

#### **Run a single command in shell environment**
```bash
./env-sh -c '<command> [<arg>...]'
```

#### **Run an interactive bash shell in shell environment**
```bash
./env-sh
```

#### **Open vscode with terminals and builds that will be in shell environment:**
```bash
code .
```
