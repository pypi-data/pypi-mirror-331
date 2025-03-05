# Glaium SDK

Install

## Classes & Methods

## Optimizer

**optimizer**(*api_token,user,pw*)

*params*: 

- api_token - Glaium API token for the organization
- user - Username (manager or owner) for the organization
- pw - Password for user login

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response: {}

**optimizer.model**( oper, name)

*params*: 

- oper - Operation type:
    - get - Load a specific Model. Current available models:
        - Mobile Gaming
        - AdTech
        - SaaS (coming soon)
        - eCommerce (coming soon)
    - set - Update or save the current systems set in a new or existent Model.
    - del - Delete a specific Model.
- name - Name for the model

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - json containing all systems (agents) from the model: {agent_name_1:agent_id_1,…agent_name_N:agent_id_N}

**optimizer.goal**(name, description, objective, constraints, resources)

*params*: 

- name - Goal name
- description - Goal description
- objective - json containing {’system’:system_id, ’target’:’metric_name’, ’comparison’: comparison operator (>, ≥, =, ≤, <) , ’outcome’: value expected, ’by’:date}
- constraints - json containing {system_id_1:conditionals,…,system_id_N:conditionals}
- resources - json containing {system_id_1:{resource_1:availability, … resource_N:availability}, … system_id_N:{resource_1:availability, … resource_N:availability}}

*return:* json {error_code:response}

- error code: 0 ok or not 0 error
- response - goal_id

## System (Agents)

**system**(oper,name)

*params:* 

- oper - Operation type: add or del
- name - Name for the system (agent)

*return:* json {error_code:response}

- error code: 0 ok or not 0 error
- response - system_id (ok) or error message

**system.config**(system_id, inputs, output, frequency, duration, constraints, resources)

*params:* 

- inputs - json containing {system_id_1:units needed,…,system_id_N:units needed}
    - units needed - An specific amount (float) or *np.inf* for all that is available
- output - json containing {’name’: output_name, ‘unity’: type of unity, ’cumulative’:yes/no for accumulation between cycles, ‘returns’; yes/no for returning units from other systems}
- frequency - when to start each cycle: ‘every hour’, ‘daily’, ‘every other day’, ‘every 1st day of month’…
- duration - max duration to use as watchdog timer.
- constraints - conditionals formula
- resources - json containing {system_id_1:{resource_1:usage, … resource_N:usage}, … system_id_N:{resource_1:usage, … resource_N:usage}}

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - None (ok) or error message

**system.optimization**(system_id )

*params:* 

- system_id

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - json containing {’next_cycle’ : cycle number, ‘next_when’: datetime to start next cycle, ‘output’ : units expected for output, ‘inputs’: {‘input_1_name’ : units suggested for input 1, … ’input_N_name’ : units suggested for input N}}

**system.start**(system_id, cycle)

*params:* 

- system_id - Id of the system (agent) starting its process
- cycle (optional) - number of cycle starting

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - None (ok) or error message

**system.stop**( system_id, status, stock, cycle)

*params:* 

- system_id - Id of the system (agent) starting its process
- status - json containing {status_type:status_msg}
    - status_type: ok, halt (motive of halting process), hands-up (requires human intervention for <status_msg>) and error (type of error)
- stock - current volume of units available in the output
- cycle (optional) - number of cycle starting

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - None (ok) or error message

**system.performance**(system_id)

*params:* 

- system_id - Id of the system (agent) requesting performance information

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - json containing {’effectiveness’:%, ‘efficiency’:%, ‘average_duration’: number of seconds}

## Data

**data.integration**( oper, integration)

*params:* 

- oper - Operation type
    - add - Add one or more new Integration(s)
    - del - Delete one or more existent Integration(s)
- integration - json containing {name:integrator,… name_N:integrator}
    - name - Name of the Integration
    - integrator - Type of the Integration. See [https://glaium.io/integrators/](https://glaium.io/integrators/) for list available. Optional for del operation.

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - None (ok) or error message

**data.pull**(metrics,dimensions,conditional,period)

*params:* 

- metrics - Numeric primitives (float)
- dimensions - Categorical primitives (string)
- conditional - formula
- period - initial and end datetimes or **temporal expressions** ("last 10 days", "end of year", "next 2 months", "yesterday", …)

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - pd.DataFrame (ok) or error message

**data.normalize**(data,primitive,how)

*params:* 

- data - pd.DataFrame
- primitive - Primitive to normalize
- how - json containing {’normalization_function’:’params’,…} with the following available functions:
    - automatic: list of terms to detect
    - custom: json containing {search_value:replace_value,…}
    - conditional: json containing {’if_condition’:value,…’else’:default_value}

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - pd.DataFrame (ok) or error message

**data.push**(data, integrations, when, frequency)

*params:* 

- data - pd.DataFrame
- integrations - list of Integrations to push data to
- when - datetime to push data to the list of integrations.
- frequency - temporal expression. Ex: ‘every hour’, ‘daily’, ‘every other day’, ‘every 1st day of month’…

*return:* json {error_code:response}

- error code: 0 (ok) or not 0 (error)
- response - None or error message
