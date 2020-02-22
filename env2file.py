#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os


def main():
    with open("", "w", encoding='utf-8') as f:
        f.write(os.environ.get("CREDENTIALS_JSON"))

    with open("", "w", encoding='utf-8') as f:
        f.write(os.environ.get("SETTINGS_YAML"))


if __name__ == "__main__":
    main()
