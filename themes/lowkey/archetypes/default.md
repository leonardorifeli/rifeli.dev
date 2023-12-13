---
title: "{{ replace .Name '-' ' ' | title }}"
date: {{ .Date }}
draft: true # Set 'false' to publish
description: ''
updated: {{ .Updated }}
updatedDate: {{ .UpdatedDate }}
categories:
  - Uncategories
tags:
  -
---

title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
