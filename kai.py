#!/usr/bin/env python3
import sys
# from kai_brain import ask_ollama
from kai_brain import ask_query


def ask():
    arg = sys.argv[1]
    response = ask_query(arg)
    print(response)




if __name__ == "__main__":
    # main()
    ask()