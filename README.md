# Wafer

Wafer is a simple but effective web application firewall (WAF) fuzzing tool. It is designed to be used as a standalone script, it uses various techniques build payloads which could potentially bypass a WAF.

## Installation

Git clone the repository and install the requirements.

```bash
git clone https://github.com/sysdig/wafer && cd wafer && pip3 install -r requirements.txt
``` 

## ChromeDriver

Wafer uses ChromeDriver to render the page and analyze the DOM. You can download latest ChromeDriver [here](https://googlechromelabs.github.io/chrome-for-testing/#stable).

## Techniques

Wafer first try to identify blocked payloads or strings by sending a list of common payloads. Then it uses various techniques to build unique payloads which could potentially trigger an XSS.

Most of the techniques are from PortSwiggers XSS cheat sheet, you can find it [here](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet).

Wafer can combine multiple techniques to build unique payloads that trigger different XSS vectors.

## Human Interaction

Some vectors require human interaction, for example, the `onmouseover` v ector requires the user to hover over the payload. Wafer will automate all the possible interactions so user doesn't have to do it manually.

## Acknowledgements

- AWS WAF Bypass (found by Wafer)