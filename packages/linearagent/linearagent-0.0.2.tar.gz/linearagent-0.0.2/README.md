# Linear Agent
This is a framework for creating simple linear agents. 
```
 LINEAR AGENT                                                                
                                                                             
 The Linear Agent is a simple framework in which each customizable tool is   
 called linearly, which uses a common context window across tool calls,
 called 'memory'.
                                                                             
 The planner provides a list of tool calls to be executed using available    
 tools. The planner primes the linear agent for the sequence of task to be   
 executed.                                                                   
                                                                             
                     ┌──────────────────────────────────────────────────────┐
┌──────────────┐     │┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐│
│              │     ││           │ │           │ │           │ │          ││
│              │     ││           │ │           │ │           │ │          ││
│   PLANNER    ┼─────►│   TOOL1   │ │    TOOL2  │ │   TOOL3   │ │   TOOL4  ││
│              │     ││           │ │           │ │           │ │          ││
│              │     ││           │ │           │ │           │ │          ││
└─────▲───┬────┘     │└───▲───┬───┘ └───▲───┬───┘ └───▲───┬───┘ └───▲──┬───┘│
      │   │          └──────────────────────────────────────────────────────┘
┌─────┼───▼───────────────┼───▼─────────┼───▼─────────┼───▼─────────┼──▼───┐ 
│                                                                          │ 
│                                                                          │ 
│                 MEMORY                              THREAD               │ 
│                                                     ======               │ 
│  Memory is a persistent dictionary/document                              │ 
│   database that populates the context, for the    SPECIAL KEY            │ 
│  subsequent tool calls.                           Provides the context   │ 
│                                                   under which the        │ 
│  Memory items are passed around tools with        linear agent was       │ 
│  'memory keys'                                    called.                │ 
│                                                                          │ 
└──────────────────────────────────────────────────────────────────────────┘ 
 ```
