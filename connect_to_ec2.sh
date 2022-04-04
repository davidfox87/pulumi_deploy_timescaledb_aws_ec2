#!/bin/bash

ssh -i .ssh/rsa ubuntu@$(pulumi stack output hostname)