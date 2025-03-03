<p align="center">
    <img width="256px" src="AetherLogIcon.png" align="center" alt="AetherLog" />
</p>

### AetherLog
---
Python pretty logging library

#### Installation

`pip install aetherlog`

#### Usage

```python
from AetherLog import AetherLogger, AetherConfig, LogLevel

#Initialize AetherLogger with config
logger = AetherLogger(AetherConfig())

#Log functions
logger.debug("Debug message", True)
logger.info("Information message", True)
logger.success("Success message", True)
logger.warn("Warning message", True)
logger.error("Error message", True)
logger.fatal("FATAL MESSAGE", True)
```