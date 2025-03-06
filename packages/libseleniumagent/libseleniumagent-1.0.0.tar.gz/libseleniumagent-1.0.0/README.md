[![CI](https://github.com/infrasonar/selenium-agent/workflows/CI/badge.svg)](https://github.com/infrasonar/selenium-agent/actions)
[![Release Version](https://img.shields.io/github/release/infrasonar/selenium-agent)](https://github.com/infrasonar/selenium-agent/releases)

# InfraSonar Selenium agent

Documentation: https://docs.infrasonar.com/collectors/agents/selenium/

## Environment variables

Environment                 | Default                       | Description
----------------------------|-------------------------------|-------------------
`TOKEN`                     | _required_                    | Token to connect to.
`ASSET_ID`                  | `/data/.asset.json`           | Asset Id _or_ file where the Agent asset Id is stored _(must be a volume mount)_.
`API_URI`                   | https://api.infrasonar.com    | InfraSonar API.
`CHECK_INTERVAL`            | `300`                         | Interval for the selenium check in seconds.
`TESTS_DIR`                 | `/data/tests`                 |
`LOG_LEVEL`                 | `warning`                     | Log level _(error, warning, info, debug)_.
`LOG_COLORIZED`             | `0`                           | Log colorized, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_FMT`                   | `%y%m...`                     | Default format is `%y%m%d %H:%M:%S`.
