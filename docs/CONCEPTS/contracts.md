# Why test the contract?

A health response crosses a boundary. The server produces JSON and a client reads it. Changing a field name can break the client even if the server still starts. The P0 tests request the endpoint and compare the published OpenAPI document with the generated definition. Try changing a response field locally, run verification, and inspect which test first explains the mismatch.
