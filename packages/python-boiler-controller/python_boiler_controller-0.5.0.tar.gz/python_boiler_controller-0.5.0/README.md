# Boiler Controller

A comprehensive boiler startup controller using Python. The application will simulate the operations of a boiler system, reflecting real-world scenarios with detailed state transitions, timers, and logging capabilities.

## Application Flow

Initially, the boiler will be in lockout state with interlock switch being open. To start the boiler, first toggle the interlock switch and start the boiler.

Boiler will enter into 3 stages for start sequence. The first stage will be pre-purge phase which will happen for 10 seconds, and then initiate phase for 10 seconds. After that, boiler will be in operational state.

We can also stop the sequence in the middle by pressing Ctrl-C during the stages.
