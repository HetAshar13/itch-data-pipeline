# HPC Access Checklist

Your HPC username is expected to be `hashar`.

## Step 1: SSH key

Generate an SSH key on Windows PowerShell if needed:

```powershell
ssh-keygen -t ed25519 -C "hashar@uni.lu"
```

Then upload the public key to the ULHPC account portal.

## Step 2: Test SSH

After key registration, test login using the local SSH alias that has already
worked for this project:

```powershell
ssh iris-cluster
```

This alias is configured locally to use:

- host: `access-iris.uni.lu`
- port: `8022`
- user: `hashar`
- identity file: `~/.ssh/ulhpc_ed25519`

If the alias is unavailable, use the explicit command:

```powershell
ssh -p 8022 -i $HOME\.ssh\ulhpc_ed25519 hashar@access-iris.uni.lu
```

The login may prompt for the SSH key passphrase/password.

Do not run heavy code on access/login nodes.

## Step 3: Check environment

Once logged in:

```bash
pwd
whoami
module avail python
module avail
squeue -u hashar
```

## Step 4: Ask/verify

- Where is the Nasdaq data located?
- Which directory should be used for intermediate outputs?
- Can you install Python packages in a virtual environment?
- Is MeatPy already installed?
- Should you use Apptainer/Singularity?
