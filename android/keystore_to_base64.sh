#!/usr/bin/env bash

# Script to remember how to encode the app's signing keystore to BASE64

openssl base64 < app/signing_keystore.jks
