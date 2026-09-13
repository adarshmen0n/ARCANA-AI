# Distributed Systems: Consensus, Fault Tolerance, and Replicated State Machines

## 1. The Distributed Consensus Problem
In distributed computing, consensus is the process of agreeing on a single data value or state among multiple participating nodes. Nodes communicate asynchronously over networks that may delay, reorder, or lose messages. The fundamental challenge is reaching agreement even when nodes fail or network partitions occur.

## 2. The FLP Impossibility Result
Fischer, Lynch, and Paterson (FLP) proved in 1985 that in an asynchronous network, no deterministic consensus protocol can guarantee both safety and liveness in the presence of even a single unannounced fail-stop crash. Consequently, practical distributed consensus protocols must make weak synchrony assumptions, use randomized timeouts, or sacrifice liveness during network partitions to guarantee safety.

## 3. The Raft Consensus Algorithm
Raft is designed specifically for understandability and operational clarity. It decomposes consensus into three independent sub-problems:
- **Leader Election**: A cluster selects a single leader node using randomized heartbeat timeouts.
- **Log Replication**: The elected leader accepts client requests, appends log entries, and forces follower nodes to replicate its log.
- **Safety**: An elected leader is guaranteed to contain all committed log entries from prior terms.

## 4. Byzantine Fault Tolerance (BFT)
Crash fault tolerance assumes failed nodes simply stop responding. Byzantine Fault Tolerance addresses adversarial environments where nodes may exhibit arbitrary or malicious behavior, such as sending conflicting messages to different peers. A system of N nodes can tolerate at most F Byzantine nodes if N >= 3F + 1. Practical Byzantine Fault Tolerance (PBFT) and modern Proof-of-Stake consensus mechanisms establish consensus under these adversarial constraints.
