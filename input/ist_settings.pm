# Input file for IST (In-System Test) configurations for MATHS-IST, RIST, and Adaptive-RIST
# Backend owner needs to fill in the data from the data source
package ist_settings;

use strict;
use warnings;

# Refer to: https://confluence.nvidia.com/display/FunctionalTeam/Input+File+Setup for details on how to setup Rules for Configuration and DataPointers
# Refer to https://confluence.nvidia.com/display/FunctionalTeam/ist_settings.pm for file spec details.

%ist_settings::data = (
	'ist_configurations' => {
        'Configuration' => {
                'Rules' => [
                    {
                        'name' => 'GR100-Engineering Rule',
                        'when' => 'BU = Engineering AND Product Type IN [Multi-GPU]',
                        'use' => 'GR100-Engineering'
                    },
					{
                        'name' => 'GR102-Engineering Rule',
                        'when' => 'BU = Engineering AND Product Type IN [Single GPU]',
                        'use' => 'GR102-Engineering'
                    },
                    {
                        'name' => 'GR100-Product Rule',
                        'when' => 'BU != Engineering AND Product Type IN [Multi-GPU]',
                        'use' => 'GR100-Product'
                    },
					{
                        'name' => 'GR102-Product Rule',
                        'when' => 'BU != Engineering AND Product Type IN [Single GPU]',
                        'use' => 'GR102-Product'
                    },
                ],
                'Default' => 'Product'
        },
		'DataPointers' => {		
			'GR100-Engineering' => {
				'MATHS-IST' => {
                    'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpuMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE2' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
                    'VFE3' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE4' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE5' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
                    'VFE6' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE7' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE8' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					}
				},
				'RIST_Base_Entry_Table' => {
					'Enable_RIST' => 1,
					'RIST_Entry_Transition_Voltage' => 900000, # Voltage in uV
					'RIST_Exit_Transition_Voltage' => 900000, # Voltage in uV
					'VFE_Variable_T0_Vmin' => 'T0_Vmin',
					'VFE_Variable_T0_Temperature' => 'T0_Temp',
					'VFE_Variable_Tau' => 'Tau',
					'Voltage_Domains' => ['NVVDDI_0', 'NVVDDI_1']
				},
				'RIST' => {
					'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','800000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					}
				},
				'RIST-Adaptive' => {
					'VFE0' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 800mV
											'Coeffs' => ['0', '0', '0', '0', '0', '800000'],
											'Variable' => ['Speedo', 'TempGpcMin']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT_Adaptive'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					}
				}
				#'MATHS-IST' => {
                #    'TestPattern0_BaseFTM_StuckAt_Vmin' => {
				#		'NVVDDI' => {
				#			'Class' => 'VFE',
				#			'InterchangeComparatorOperands' => 'Yes',
				#			'ISTModeName' => 'BaseFTM_StuckAt_Vmin',
				#			'Equation' => [
				#				{
				#					'Coeffs' => ['0.00339019999477816','0.253035099282948','-0.697752899993537','-338.591250409728','1588.00700001505','1648629.50107558'],
				#					'Variable' => ['Speedo', 'Temperature']
				#				}
				#			],
				#			'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
				#			'Thermeqtype' => 'IST_Curves'
				#		},
				#		'MSVDDI' => {
				#			'Class' => 'VFE',
				#			'InterchangeComparatorOperands' => 'Yes',
				#			'ISTModeName' => 'BaseFTM_StuckAt_Vmin',
				#			'Equation' => [
				#				{
				#					'Coeffs' => ['0.00339019999477816','0.253035099282948','-0.697752899993537','-338.591250409728','1588.00700001505','1648629.50107558'], #C5, C4, C3, C2, C1, C0
				#					'Variable' => ['Speedo', 'Temperature']
				#				}
				#			],
				#			'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
				#			'Thermeqtype' => 'IST_Curves'
				#		}
				#	},
                #    'TestPattern1_BaseFTM2CLK_P8' => {
				#		'NVVDDI' => {
				#			'Class' => 'VFE',
				#			'InterchangeComparatorOperands' => 'Yes',
				#			'ISTModeName' => 'BaseFTM2CLK_P8',
				#			'Equation' => [
				#				{
				#					'Coeffs' => ['0.00339019999477816','0.253035099282948','-0.697752899993537','-338.591250409728','1588.00700001505','1648629.50107558'], #C5, C4, C3, C2, C1, C0
				#					'Variable' => ['Speedo', 'Temperature']
				#				}
				#			],
				#			'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
				#			'Thermeqtype' => 'IST_Curves'
				#		},
				#		'MSVDDI' => {
				#			'Class' => 'VFE',
				#			'InterchangeComparatorOperands' => 'Yes',
				#			'ISTModeName' => 'BaseFTM2CLK_P8',
				#			'Equation' => [
				#				{
				#					'Coeffs' => ['0.00339019999477816','0.253035099282948','-0.697752899993537','-338.591250409728','1588.00700001505','1648629.50107558'], #C5, C4, C3, C2, C1, C0
				#					'Variable' => ['Speedo', 'Temperature']
				#				}
				#			],
				#			'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
				#			'Thermeqtype' => 'IST_Curves'
				#		}
				#	}					
				#}
			},
			'GR102-Engineering' => {
				'MATHS-IST' => {
                    'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpuMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE2' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
                    'VFE3' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE4' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE5' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
                    'VFE6' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE7' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE8' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					}
				},
				'RIST_Base_Entry_Table' => {
					'Enable_RIST' => 1,
					'RIST_Entry_Transition_Voltage' => 900000, # Voltage in uV
					'RIST_Exit_Transition_Voltage' => 900000, # Voltage in uV
					'VFE_Variable_T0_Vmin' => 'T0_Vmin',
					'VFE_Variable_T0_Temperature' => 'T0_Temp',
					'VFE_Variable_Tau' => 'Tau',
					'Voltage_Domains' => ['NVVDDI']
				},
				'RIST' => {
					'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','800000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					}
				},
				'RIST-Adaptive' => {
					'VFE0' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 800mV
											'Coeffs' => ['0', '0', '0', '0', '0', '800000'],
											'Variable' => ['Speedo', 'TempGpcMin']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT_Adaptive'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					}
				}
			},
			'GR100-Product' => {
				'MATHS-IST' => {
                    'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpuMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE2' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
                    'VFE3' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE4' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE5' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
                    'VFE6' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE7' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE8' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					}
				},
				'RIST_Base_Entry_Table' => {
					'Enable_RIST' => 1,
					'RIST_Entry_Transition_Voltage' => 900000, # Voltage in uV
					'RIST_Exit_Transition_Voltage' => 900000, # Voltage in uV
					'VFE_Variable_T0_Vmin' => 'T0_Vmin',
					'VFE_Variable_T0_Temperature' => 'T0_Temp',
					'VFE_Variable_Tau' => 'Tau',
					'Voltage_Domains' => ['NVVDDI_0', 'NVVDDI_1']
				},
				'RIST' => {
					'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','800000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT','CAS_STUCKAT','SA_FS_STUCKAT','SA_BR_STUCKAT','FTM_PLL_P8','FTM_PLL_P0L','FTM_ALLSEQ_PLL_P8','FTM_ALLSEQ_PLL_P0L','CAD_PLL_P8','CAD_PLL_P0L','SDD_PLL_P8','SDD_PLL_P0L','FTM_BR_PLL_P8','FTM_BR_PLL_P0L','MBIST_BYP_WAplusRA_STUCKAT','MBIST_BYP_WAplusRASlowSVOP_STUCKAT','MBIST_BYP_RA_STUCKAT','MBIST_PLL_P8','MBIST_PLL_P0L'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','950000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['FTM_PLL_P0M_LT','FTM_PLL_P0M_HT','FTM_PLL_P0H_LT','FTM_PLL_P0H_HT','FTM_ALLSEQ_PLL_P0M_LT','FTM_ALLSEQ_PLL_P0M_HT','FTM_ALLSEQ_PLL_P0H_LT','FTM_ALLSEQ_PLL_P0H_HT','CAD_PLL_P0M_LT','CAD_PLL_P0M_HT','CAD_PLL_P0H_LT','CAD_PLL_P0H_HT','SDD_PLL_P0M_LT','SDD_PLL_P0M_HT','SDD_PLL_P0H_LT','SDD_PLL_P0H_HT','FTM_BR_PLL_P0M_LT','FTM_BR_PLL_P0M_HT','FTM_BR_PLL_P0H_LT','FTM_BR_PLL_P0H_HT','MBIST_PLL_P0M_LT','MBIST_PLL_P0M_HT','MBIST_PLL_P0H_LT','MBIST_PLL_P0H_HT'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					}
				},
				'RIST-Adaptive' => {
					'VFE0' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 800mV
											'Coeffs' => ['0', '0', '0', '0', '0', '800000'],
											'Variable' => ['Speedo', 'TempGpcMin']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT_Adaptive','CAS_STUCKAT_Adaptive','SA_FS_STUCKAT_Adaptive','SA_BR_STUCKAT_Adaptive','FTM_PLL_P8_Adaptive','FTM_PLL_P0L_Adaptive','FTM_ALLSEQ_PLL_P8_Adaptive','FTM_ALLSEQ_PLL_P0L_Adaptive','CAD_PLL_P8_Adaptive','CAD_PLL_P0L_Adaptive','SDD_PLL_P8_Adaptive','SDD_PLL_P0L_Adaptive','FTM_BR_PLL_P8_Adaptive','FTM_BR_PLL_P0L_Adaptive','MBIST_BYP_WAplusRA_STUCKAT_Adaptive','MBIST_BYP_WAplusRASlowSVOP_STUCKAT_Adaptive','MBIST_BYP_RA_STUCKAT_Adaptive','MBIST_PLL_P8_Adaptive','MBIST_PLL_P0L_Adaptive'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 950mV
											'Coeffs' => ['0', '0', '0', '0', '0', '950000'],
											'Variable' => ['Speedo', 'TempGpcAvg']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['FTM_PLL_P0M_LT_Adaptive','FTM_PLL_P0M_HT_Adaptive','FTM_PLL_P0H_LT_Adaptive','FTM_PLL_P0H_HT_Adaptive','FTM_ALLSEQ_PLL_P0M_LT_Adaptive','FTM_ALLSEQ_PLL_P0M_HT_Adaptive','FTM_ALLSEQ_PLL_P0H_LT_Adaptive','FTM_ALLSEQ_PLL_P0H_HT_Adaptive','CAD_PLL_P0M_LT_Adaptive','CAD_PLL_P0M_HT_Adaptive','CAD_PLL_P0H_LT_Adaptive','CAD_PLL_P0H_HT_Adaptive','SDD_PLL_P0M_LT_Adaptive','SDD_PLL_P0M_HT_Adaptive','SDD_PLL_P0H_LT_Adaptive','SDD_PLL_P0H_HT_Adaptive','FTM_BR_PLL_P0M_LT_Adaptive','FTM_BR_PLL_P0M_HT_Adaptive','FTM_BR_PLL_P0H_LT_Adaptive','FTM_BR_PLL_P0H_HT_Adaptive','MBIST_PLL_P0M_LT_Adaptive','MBIST_PLL_P0M_HT_Adaptive','MBIST_PLL_P0H_LT_Adaptive','MBIST_PLL_P0H_HT_Adaptive'],
						'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
						'Thermeqtype' => 'Vmin_Curves'
					},
				}				
			},
			'GR102-Product' => {
				'MATHS-IST' => {
                    'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
								'Variable' => ['Speedo', 'TempGpuMin']
							}
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE2' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','-322.801','0','1334105'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM_StuckAt_Vmin', 'BaseFTM2CLK_P8','FseqRAMSeq_P8','Bridging_P8','CAD_P8','SDD_P8','Fseq_Stuckat_Vmin','Bridging_Stuckat_Vmin','CAS_Stuckat_Vmin','MBIST_P8_LVA','MBIST_P8_NA','MBIST_P8_HVA','MBIST_Bypass_LVA_Vmin','MBIST_Bypass_NA_Vmin','MBIST_Bypass_HVA_Vmin'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
                    'VFE3' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE4' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','900000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE5' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','900000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0L','BaseFTM2CLK_P0M_LT','BaseFTM2CLK_P0M_HT','FseqRAMSeq_P0L','FseqRAMSeq_P0M_LT','FseqRAMSeq_P0M_HT','Bridging_P0L','Bridging_P0M_LT','Bridging_P0M_HT','CAD_P0L','CAD_P0M_LT','CAD_P0M_HT','SDD_P0L','SDD_P0M_LT','SDD_P0M_HT','MBIST_P0L','MBIST_P0M_LT','MBIST_P0M_HT'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
                    'VFE6' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE7' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','1000000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpuAvg']
							}
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['MSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					},
					'VFE8' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'MinMax' => {
									'Type' => 'Max',
									'Equation' => [
										# Operand 1: ION die equation - Uses Speedo and IO North die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoNAvg'],
											'Comment' => 'ION die voltage requirement'# Optional: Add descriptive comment
										},
										# Operand 2: IOS die equation - Uses Speedo and IO South die average temperature
										{
											'Coeffs' => ['0','0','0','0','0','1000000'], #X^2,Y^2,XY,X,Y,Const
											'Variable' => ['Speedo', 'TempIoSAvg'],
											'Comment' => 'IOS die voltage requirement'# Optional: Add descriptive comment
										}
									]
								}
							},
						],
						'ISTModeNames' => ['BaseFTM2CLK_P0H_LT','BaseFTM2CLK_P0H_HT','FseqRAMSeq_P0H_LT','FseqRAMSeq_P0H_HT','Bridging_P0H_LT','Bridging_P0H_HT','CAD_P0H_LT','CAD_P0H_HT','SDD_P0H_LT','SDD_P0H_HT','MBIST_P0H_LT','MBIST_P0H_HT','MBIST_Bypass_LVA_Vmax','MBIST_Bypass_NA_Vmax','MBIST_Bypass_HVA_Vmax','MBIST_P0H_LT_Vmax','MBIST_P0H_HT_Vmax','BaseFTM_Stuckat_Vmax','BaseFTM_P0H_LT_Vmax','BaseFTM_P0H_HT_Vmax'],
						'VoltageDomains' => ['SYSVDDI'],
						'Thermeqtype' => 'VF_Curves'
					}
				},	
				'RIST_Base_Entry_Table' => {
					'Enable_RIST' => 1,
					'RIST_Entry_Transition_Voltage' => 900000, # Voltage in uV
					'RIST_Exit_Transition_Voltage' => 900000, # Voltage in uV
					'VFE_Variable_T0_Vmin' => 'T0_Vmin',
					'VFE_Variable_T0_Temperature' => 'T0_Temp',
					'VFE_Variable_Tau' => 'Tau',
					'Voltage_Domains' => ['NVVDDI']
				},
				'RIST' => {
					'VFE0' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','800000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcMin']
							}
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT','CAS_STUCKAT','SA_FS_STUCKAT','SA_BR_STUCKAT','FTM_PLL_P8','FTM_PLL_P0L','FTM_ALLSEQ_PLL_P8','FTM_ALLSEQ_PLL_P0L','CAD_PLL_P8','CAD_PLL_P0L','SDD_PLL_P8','SDD_PLL_P0L','FTM_BR_PLL_P8','FTM_BR_PLL_P0L','MBIST_BYP_WAplusRA_STUCKAT','MBIST_BYP_WAplusRASlowSVOP_STUCKAT','MBIST_BYP_RA_STUCKAT','MBIST_PLL_P8','MBIST_PLL_P0L'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Class' => 'VFE',
						'InterchangeComparatorOperands' => 'Yes',
						'Equation' => [
							{
								'Coeffs' => ['0','0','0','0','0','950000'], #C5, C4, C3, C2, C1, C0
								'Variable' => ['Speedo', 'TempGpcAvg']
							}
						],
						'ISTModeNames' => ['FTM_PLL_P0M_LT','FTM_PLL_P0M_HT','FTM_PLL_P0H_LT','FTM_PLL_P0H_HT','FTM_ALLSEQ_PLL_P0M_LT','FTM_ALLSEQ_PLL_P0M_HT','FTM_ALLSEQ_PLL_P0H_LT','FTM_ALLSEQ_PLL_P0H_HT','CAD_PLL_P0M_LT','CAD_PLL_P0M_HT','CAD_PLL_P0H_LT','CAD_PLL_P0H_HT','SDD_PLL_P0M_LT','SDD_PLL_P0M_HT','SDD_PLL_P0H_LT','SDD_PLL_P0H_HT','FTM_BR_PLL_P0M_LT','FTM_BR_PLL_P0M_HT','FTM_BR_PLL_P0H_LT','FTM_BR_PLL_P0H_HT','MBIST_PLL_P0M_LT','MBIST_PLL_P0M_HT','MBIST_PLL_P0H_LT','MBIST_PLL_P0H_HT'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					}
					
				},
				'RIST-Adaptive' => {
					'VFE0' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 800mV
											'Coeffs' => ['0', '0', '0', '0', '0', '800000'],
											'Variable' => ['Speedo', 'TempGpcMin']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['SA_BASE_STUCKAT_Adaptive','CAS_STUCKAT_Adaptive','SA_FS_STUCKAT_Adaptive','SA_BR_STUCKAT_Adaptive','FTM_PLL_P8_Adaptive','FTM_PLL_P0L_Adaptive','FTM_ALLSEQ_PLL_P8_Adaptive','FTM_ALLSEQ_PLL_P0L_Adaptive','CAD_PLL_P8_Adaptive','CAD_PLL_P0L_Adaptive','SDD_PLL_P8_Adaptive','SDD_PLL_P0L_Adaptive','FTM_BR_PLL_P8_Adaptive','FTM_BR_PLL_P0L_Adaptive','MBIST_BYP_WAplusRA_STUCKAT_Adaptive','MBIST_BYP_WAplusRASlowSVOP_STUCKAT_Adaptive','MBIST_BYP_RA_STUCKAT_Adaptive','MBIST_PLL_P8_Adaptive','MBIST_PLL_P0L_Adaptive'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
					'VFE1' => {
						'Equation' => [
							{
								# VFE 0: Comparison entry - Check T0_Vmin > 0.0001uV - if True - evaluate Vmin = T0_Vmin + T0_Temp*Temp coefficient (in uV), else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '0.0001',
											'DataValidMax' => ''
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 1: Base from T0_Vmin - C1*T0_Vmin (Eg: 1*T0_Vmin)
											'Coeffs' => ['0', '1', '0'], # C2, C1, C0
											'Variable' => 'T0_Vmin'
										},
										{
											# VFE 2: Temp Offset - C1*T0_Temp (Eg: 20*T0_Temp)
											'Coeffs' => ['0', '20', '0'], # C2, C1, C0
											'Variable' => 'T0_Temp'
										}
									]
								}
							},
							{
								# VFE 0: Comparison entry - Check T0_Vmin < 0.0001uV - if True - calculate baseline from equation, else do nothing
								'Comparison' => {
									'Criteria' => {
										'0' => {
											'DataValidVariable' => 'T0_Vmin',
											'DataValidMin' => '',
											'DataValidMax' => '0.0001'
										}
									},
									# TRUE branch: VFE 1 and VFE 2
									'Equation' => [
										{ 
											# VFE 3: Base from Equation (Speedo, Temperature) - FALSE path alternative - eg: 950mV
											'Coeffs' => ['0', '0', '0', '0', '0', '950000'],
											'Variable' => ['Speedo', 'TempGpcAvg']
										}
									]
								}
							},
							{
								# VFE 4: Aging Offsets (Tau, Aging) - Aging Variation and Average Aging offset = C0 + (C1 * Tau) - eg: 10000 + (0.1*Tau) - 10mV aging variation+tau based aging
								'Coeffs' => ['0', '0.1', '10000'], # C2, C1, C0
								'Variable' => 'Tau'
							},
							{ #Intermittency and Temperature Offset - CurrentTemperature*Temp coefficient + Intermittency Offset (eg: Temp coeffecient = 20 in opposite direction), Intermittency=10mV
								'Coeffs' => ['0', '-20', '10000'], #C2, C1, C0
								'Variable' => 'TempGpcMin'
								
							}
							# { #Aging Variation
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# },							
							# { #CYA
								# 'Coeffs' => ['0', '0', '0'], #C2, C1, C0
								# 'Variable' => 'Speedo'
							# }							
						],
						'ISTModeNames' => ['FTM_PLL_P0M_LT_Adaptive','FTM_PLL_P0M_HT_Adaptive','FTM_PLL_P0H_LT_Adaptive','FTM_PLL_P0H_HT_Adaptive','FTM_ALLSEQ_PLL_P0M_LT_Adaptive','FTM_ALLSEQ_PLL_P0M_HT_Adaptive','FTM_ALLSEQ_PLL_P0H_LT_Adaptive','FTM_ALLSEQ_PLL_P0H_HT_Adaptive','CAD_PLL_P0M_LT_Adaptive','CAD_PLL_P0M_HT_Adaptive','CAD_PLL_P0H_LT_Adaptive','CAD_PLL_P0H_HT_Adaptive','SDD_PLL_P0M_LT_Adaptive','SDD_PLL_P0M_HT_Adaptive','SDD_PLL_P0H_LT_Adaptive','SDD_PLL_P0H_HT_Adaptive','FTM_BR_PLL_P0M_LT_Adaptive','FTM_BR_PLL_P0M_HT_Adaptive','FTM_BR_PLL_P0H_LT_Adaptive','FTM_BR_PLL_P0H_HT_Adaptive','MBIST_PLL_P0M_LT_Adaptive','MBIST_PLL_P0M_HT_Adaptive','MBIST_PLL_P0H_LT_Adaptive','MBIST_PLL_P0H_HT_Adaptive'],
						'VoltageDomains' => ['NVVDDI'],
						'Thermeqtype' => 'Vmin_Curves'
					},
				}		
			},
		},	
	}
);

%ist_settings::globals = (
	'IST_Default_Configuration' => {
		'Enable_IST' => '1',
		'IST_Mode' => 'Continuous',
		'Log_Level' => 'INFO',
	},
	'IST_Error_Codes' => {
		'IST_VALIDATION_FAILED' => '0x1001',
		'IST_DISABLED' => '0x1002',
		'IST_TIMEOUT' => '0x1003',
	},
);

1;
