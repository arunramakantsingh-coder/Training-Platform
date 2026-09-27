# Lab EVE API

EVE-specific control service for the Training Platform.

Boundary: Training Website -> Lab Controller -> Lab Interface -> Lab Connector -> Lab EVE API -> EVE-NG.

The service runs inside the EVE-NG VM so EVE-specific filesystem paths, native wrappers, local permissions, and future EVE API usage remain behind one controlled contract.

The implementation deliberately does not assume an EVE Web login endpoint. Native lifecycle command mappings will be enabled only after the installed EVE-NG wrapper syntax is verified.
