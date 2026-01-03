#!/bin/bash

# ==================================================================================================================================================================================================================
# Skript:       ConformationLab_env_Generator.sh
# Use:          Automatic Installation of ConformationLab Environment, installation of ColabFold and export of the Environment for Generating ConformationLab Studio
# Author:       Spike Murphy Müller
# Date:         2025-09-29
# Copyright:    
# ==================================================================================================================================================================================================================
# prerequisite: Miniconda Anaconda was installed
# prerequisite: Command Line Developer Tools installed
# ==================================================================================================================================================================================================================


# ===== installation of anaconda ===================================================================================================================================================================================
# 
# installation of Anaconda Miniconda: 
# visite the official website, download and install the program:
# link: https://www.anaconda.com/download/success
#
# ==================================================================================================================================================================================================================


# ====== installation of Command Line Developer Tools ==============================================================================================================================================================
#
# open the mac's Terminal by clicking 'command + space', typing 'Terminal' in the search tool, and clicking on 'Terminal'
# enter: xcode-select -p
# you will get either the directory (~/example/example) or an error
# if there is an error proceed with installation (next line) otherwise the tool is already installed, so proceed with executing the script:
# enter: xcode-select --install
# ===================================================================================================================================================================================================================


# ===== running the script ==========================================================================================================================================================================================
# 
# open the mac's Terminal by klicking 'command + space', typing 'Terminal' in the search tool, and clicking on 'Terminal'
# move skript into the downloads folder
# to make skript executable enter: 		chmod +x ~/Downloads/ConformationLab_env_Generator.sh
# to start running the script enter:		~/Downloads/ConformationLab_env_Generator.sh
#
# ===================================================================================================================================================================================================================

echo ">>>>>>>>>> create environment named 'conflab' with python 3.10"
conda create -y -n conflab python=3.10

echo ">>>>>>>>>> load conda initialization script into current shell"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate conflab

echo ">>>>>>>>>> installing ColabFold with AlphaFold support"
pip install "colabfold[alphafold]"

echo ">>>>>>>>>> reinstalling a CPU-only compatible version of JAX"
pip uninstall -y jax jaxlib ml-dtypes absl-py chex
pip install --no-cache-dir "jax[cpu]==0.4.20" "jaxlib==0.4.20" "ml-dtypes==0.2.0" "absl-py==1.4.0" "chex==0.1.81"

echo ">>>>>>>>>> installing the hhsearch package (for --templates)"
conda install -y -c conda-forge -c bioconda hhsuite

echo ">>>>>>>>>> installing PDBfixer for fixing output files"
conda install -y -c conda-forge pdbfixer

echo ">>>>>>>>>> installing scientific libraries (supported versions, last to avoid automatic updates and mismatches)"
pip install --force-reinstall --no-cache-dir "numpy==1.26.4" "pandas==1.5.3" "scipy==1.13.1"  "biopython==1.82"

echo ">>>>>>>>>> rebranding binary: adding conflab_batch"
cd $CONDA_PREFIX/bin
cp colabfold_batch conflab_batch

echo ">>>>>>>>>> installing pywebview for mol*viewer"
pip install pywebview

echo ">>>>>>>>>> installing psutil for system stats (CPU/RAM)"
pip install psutil

echo ">>>>>>>>>> installing tkinterdnd2 for drag and drop (not done for M1)"
pip install tkinterdnd2

echo ">>>>>>>>>> installing pyinstaller"
conda install -y -c conda-forge pyinstaller

echo ">>>>>>>>>> installing authlib for Auth0 Login"
pip install flask authlib requests

echo ">>>>>>>>>> installing packing package"
conda install -y -c conda-forge conda-pack

echo ">>>>>>>>>> going to where the environment pack should be saved"
cd ~/ConformationLabGeneration

echo ">>>>>>>>>> packing environment into tar.gz"
conda pack -n conflab -o conflab_env.tar.gz

cat <<EOF
>>>>>>>>>> pause for file organisation

   Please place the following files into ~/ConformationLabGeneration:

   Python Scripts:
   - ConformationLabStudio_v1.12.py
   - run_molstar_v1.0.py
   - run_login_orcid_v1.0.py
   - run_login_auth0_v1.0.py

   Environment:
   - conflab_env.tar.gz

   Further Files:
   - ConformationLabStudio.spec
   - ConformationLabLogo.png
   - ConformationLabIcon.icns

   License Files:
   - LICENSE_ConformationLabStudio.txt
   - LICENSE_AlphaFold2.txt
   - LICENSE_ColabFold.txt
   - ABOUT.txt
   - DISCLAIMER.txt
   - LEGAL.txt
   - TERMS.txt
   - PRIVACY.txt

EOF

while true; do
    read -rp "Are all the necessary files moved? (y/n): " answer
    case "$answer" in
        [Yy]) echo "Continuing..."; break ;;
        [Nn]) echo "Please place the files in this folder before continuing."; exit 1 ;;
        *)    echo "Please answer y or n." ;;
    esac
done

while true; do
    echo ">>>>>>>>>> Checking for required files..."
    required_files=(
        "ConformationLabStudio_v1.12.py"
        "run_molstar_v1.0.py"	
        "run_login_orcid_v1.0.py"
	    "run_login_auth0_v1.0.py"
        "conflab_env.tar.gz"
        "ConformationLabStudio.spec"
        "ConformationLabLogo.png"
        "ConformationLabIcon.icns"
	"ABOUT.txt"
	"DISCLAIMER.txt"
        "LICENSE_ConformationLabStudio.txt"
        "LICENSE_AlphaFold2.txt"
        "LICENSE_ColabFold.txt"
        "LEGAL.txt"
        "TERMS.txt"
        "PRIVACY.txt"
    )
    missing_files=()
    for file in "${required_files[@]}"; do
        if [[ ! -e "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        echo "All files found. Continuing..."
        break
    else
        echo "ERROR: The following files are missing in $(pwd):"
        for f in "${missing_files[@]}"; do
            echo " - $f"
        done
        echo ""
	echo "Please place the missing files and then continue..."
        read -rp "Have you placed the missing files? (y/n): " confirm
        case "$confirm" in
            [Yy]) 
                echo "Rechecking..."
                ;;
            [Nn]) 
                echo "Exiting. Please rerun the script once files are ready."
                exit 1
                ;;
            *) 
                echo "Please answer y or n."
                ;;
        esac
    fi
done

echo ">>>>>>>>>> generating application"
pyinstaller ConformationLabStudio.spec

echo "
===================================================================================================
===================================== installation completed ======================================
===================================================================================================
"
echo "*INFO* for each new session activate the 'conflab' environment before running any modelling with the command: conda activate conflab *INFO*"
echo "*INFO* command for running a protein structure prediction can be found in the script when opening in textEDIT                        *INFO*"

# ===================================================================================================================================================================================================================
# for each new session activate conflab environment before running any modelling
# ===================================================================================================================================================================================================================


# ===== deinstallation of 'conflab' ================================================================================================================================================================================
# 
# open the mac's Terminal by clicking 'command + space', typing 'Terminal' in the search tool, and clicking on 'Terminal'
# when still in conflab environment enter: conda deactivate
# enter: conda env remove -n conflab
#
# ====================================================================================================================================================================================================================


# aus termianal installieren
# conda activate conflab
# cd ~/ConformationLabGeneration
# pyinstaller ConformationLabStudio.spec

# app aus terminal starten
# cd ~/ConformationLabGeneration/dist
# ./ConformationLabStudio
# lsof -i :5001
# kill -9 PID
