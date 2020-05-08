################################################################################
# IO constraints
################################################################################
# clk100:0
set_property LOC J19 [get_ports clk100]
set_property IOSTANDARD LVCMOS33 [get_ports clk100]

# clkslow:0
set_property LOC L19 [get_ports clkslow]
set_property IOSTANDARD LVCMOS33 [get_ports clkslow]

# button:0
set_property LOC F18 [get_ports button]
set_property IOSTANDARD LVCMOS33 [get_ports button]

# led:0
set_property LOC J20 [get_ports led]
set_property IOSTANDARD LVCMOS33 [get_ports led]

################################################################################
# Design constraints
################################################################################

################################################################################
# Clock constraints
################################################################################


################################################################################
# False path constraints
################################################################################


set_false_path -quiet -through [get_nets -hierarchical -filter {mr_ff == TRUE}]

set_false_path -quiet -to [get_pins -filter {REF_PIN_NAME == PRE} -of_objects [get_cells -hierarchical -filter {ars_ff1 == TRUE || ars_ff2 == TRUE}]]

set_max_delay 2 -quiet -from [get_pins -filter {REF_PIN_NAME == C} -of_objects [get_cells -hierarchical -filter {ars_ff1 == TRUE}]] -to [get_pins -filter {REF_PIN_NAME == D} -of_objects [get_cells -hierarchical -filter {ars_ff2 == TRUE}]]