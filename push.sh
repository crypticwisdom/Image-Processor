#! /bin/bash
echo "Pushing Started !"

git status
git remote -v
git remote set-url origin https://github.com/crypticwisdom/Image-Processor.git
echo "Started pushing to"
git remote -v
git status
git add .
echo "Enter a commit message: "
read msg
git commit -m "$msg"
echo "What branch are you pushing to ?"
read branch
git push origin branch

git remote set-url origin https://gitlab.com/tm30/payarenamall/e-commerce/backend.git
git remote -v


