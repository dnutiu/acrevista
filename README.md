### Django Application: Ac Revista

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/52422b3e9f00467db7f6f50e0509bb8b)](https://www.codacy.com/app/Metonimie/acrevista?utm_source=github.com&utm_medium=referral&utm_content=Metonimie/acrevista&utm_campaign=badger)

This application was written for **Python 3**.

Requirements
============
```
pip install -r requirements.txt
sudo apt-get install libmagic-dev 
```

Docummentation
==============

This app allows users to submit, review and view papers. It features Django CMS which
allows easy editing of newly created pages.

## User Group
* **Editors**: Those guys are admins over the site. They can add users, delete users,
add editors, add reviewers, create, modify or delete papers.
They can also post 'Editor' reviews on papers.

* **Reviewers** Those users are assigned to papers by an editor. The paper on which they are assigned
will appear on the account menu. The reviewers can post reviews on the paper, reviews
which are seen only by the editor.

* **Users** Users can submit papers and view editor reviews on their own papers if there is any.


#### How to add an editor?
1. Go to admin
2. Click USERS and select the desired user.
3. Check 'Staff status' and save.

#### How to add an reviewer?
1. Go to admin
2. Click PAPERS and the select the desired paper.
3. Find 'REVIEWERS:' and highlight the users which you want to be reviewers. And finally save.
