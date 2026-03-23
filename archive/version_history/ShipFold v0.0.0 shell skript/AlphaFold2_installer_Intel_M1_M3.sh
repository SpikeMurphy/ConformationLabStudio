#!/bin/bash

# ==================================================================================================================================================================================================================
# Skript:       AlphaFold2_installer_Intel_M1_M3.sh
# Use:          automatic installation of ColabFold[AlphaFold]
# Author:       Spike Murphy Müller
# Date:         2025-09-21
# Copyright:    
# ==================================================================================================================================================================================================================
#
# ColabFold[AlphaFold] installation script for macOS
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
#
# ===================================================================================================================================================================================================================


# ===== running the script ==========================================================================================================================================================================================
# 
# open the mac's Terminal by klicking 'command + space', typing 'Terminal' in the search tool, and clicking on 'Terminal'
# move skript into the downloads folder
# to make skript executable enter: 		chmod +x ~/Downloads/AlphaFold2_installer_Intel_M1_M3.sh
# to start running the script enter:		~/Downloads/AlphaFold2_installer_Intel_M1_M3.sh
#
# ===================================================================================================================================================================================================================

echo ">>>>>>>>>> create environment named 'shipfold' with python 3.10 and compatibility with AlphaFold"
conda create -y -n shipfold python=3.10

echo ">>>>>>>>>> load conda initialization script into current shell"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate shipfold

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

echo ">>>>>>>>>> rebranding binary: adding shipfold_batch"
cd ~/miniconda3/envs/shipfold/bin
cp colabfold_batch shipfold_batch

echo "
===================================== installation completed ======================================
"
echo "
============================================= summary =============================================
***												***
*** environment named 'shipfold' with python 3.10 and compatibility with AlphaFold created  	***
*** conda initialization script loaded into current shell 					***     
*** ColabFold with AlphaFold support installed 							***
*** JAX deinstalled 										***
*** CPU-only compatible version of JAX installed 						***
*** hhsearch package installed 									***        
*** PDBfixer for fixing output files installed 							***
*** scientific libraries installed 								***          
*** installation completed 									***
***												***
============================================= summary =============================================
"
echo "*INFO* for each new session activate the 'shipfold' environment before running any modelling with the command: conda activate shipfold *INFO*"
echo "*INFO* command for running a protein structure prediction can be found in the script when opening in textEDIT                           *INFO*"

# ===================================================================================================================================================================================================================
# for each new session activate shipfold environment before running any modelling
# ===================================================================================================================================================================================================================
# 
# HOW TO RUN A MODEL:
#
#
# Command for activating the shipfold environment: conda activate shipfold
# command for modelling: colabfold_batch a b --num-relax c --num-recycle d --num-seeds e --max-msa f:f --model-type g --templates --pair-mode i --msa-mode j --rank k 
# 
#
#legend:
#	a = 			input file path (e.g. ~/AlphaFold2/FASTA/ProteinName.fasta)
#	b =			output file path (e.g. ./AlphaFold2/Results/ProteinName)
#	num-relax c = 		number of relaxation steps should be set to '0' due to CPU limitations
#	num-recycle d =		number of times the five models each are repeated, start with 3 and increase as necessary according to hardware limitations
#	num-seeds e =		number of times the whole process is repeated, start with 1 (and increase as necessary according to hardware limitations)
#	max-msa f:f =		f ∈ {2n | n ∈ ℕ} -> set to powers of 2; a good initial choice is 32:32 to avoid exceeding memory limits
#	model-type g =		'alphafold2_ptm' for single polypeptide chains; 'alphafold2_multimer_v3' for protein complexes
#	templates 		include --templates to allow the model to bias towards protein database (PDB) structures, otherwise do not include
#	pair-mode i =		can be set to 'unpaired', 'paired' or 'unpaired_paired', however 'unpaired_paired' is usually recommended
#	msa-mode j =		should be set to 'mmseqs2_uniref' to avoid exhausting memory 
#				can be set to mmseqs2_uniref_env, which searches UniRef30 and environmental metagenomic databases
#	rank k =		'plddt' for single protein chains and 'multimer' for multimers
#	stop-at-score l		should not be included
#				l ∈ [1,100] ∩ ℤ -> set to 1-100 to stop modeling at a desired average model confidence for pLDDT
#
#
# EXAMPLE:
# 
# conda activate shipfold
# colabfold_batch ~/AlphaFold2/FASTA/GFP.fasta AlphaFold2/Results/GFP --num-relax 0 --num-recycle 3 --num-seeds 1 --max-msa 32:32 --model-type alphafold2_ptm --templates --pair-mode unpaired_paired --msa-mode mmseqs2_uniref --rank plddt
#
# ===================================================================================================================================================================================================================



# ===== renaming colabfold_batch ====================================================================================================================================================================================
# 
# conda activate shipfold
# cd ~/miniconda3/envs/ShipFold/bin
# cp colabfold_batch shipfold_batch
#
# ===================================================================================================================================================================================================================



# ===== deinstallation of 'shipfold' ================================================================================================================================================================================
# 
# open the mac's Terminal by clicking 'command + space', typing 'Terminal' in the search tool, and clicking on 'Terminal'
# when still in shipfold environment enter: conda deactivate
# enter: conda env remove -n shipfold
#
# ====================================================================================================================================================================================================================
