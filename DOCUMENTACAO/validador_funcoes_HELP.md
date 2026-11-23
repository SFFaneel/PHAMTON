# Referência de Funções

## Índice

- [referencias_incr](#funcao-1)
- [gravar_agregado_incr](#funcao-2)
- [consolidar_agregados_incr](#funcao-3)
- [analisar_vf_agregado_incr](#funcao-4)
- [analisar_agregados_incr](#funcao-5)
- [gerar_alertas_incr_vf_agregados](#funcao-6)
- [gerar_alertas_incr_agregados](#funcao-7)
- [validar_vnr_voc_ipca](#funcao-8)
- [validar_incr_bloco](#funcao-9)
- [validar_duplicidades_global](#funcao-10)
- [conv_flut](#funcao-11)
- [digitos](#funcao-12)
- [anl_lcmt](#funcao-13)
- [calc_digito](#funcao-14)
- [validar_CNPJ](#funcao-15)
- [val_dt](#funcao-16)
- [validar_decimal](#funcao-17)
- [validar_lista](#funcao-18)
- [validar_data](#funcao-19)
- [validar_texto](#funcao-20)
- [validar_inteiro](#funcao-21)
- [validar_projeto_pep](#funcao-22)
- [validar_tuc_ti](#funcao-23)
- [validar_tucs_proibidos](#funcao-24)
- [validar_cabos](#funcao-25)
- [validar_administracao](#funcao-26)
- [validar_torre_poste](#funcao-27)
- [validar_FLG_PER](#funcao-28)
- [validar_cm](#funcao-29)
- [validar_ti_distribuicao](#funcao-30)
- [validar_bem_individual](#funcao-31)
- [localizar_arquivo](#funcao-32)
- [_decimal_incr](#funcao-33)
- [_validar_dominio_bpr](#funcao-34)
- [ler_dados_csv](#funcao-35)
- [validar_lote](#funcao-36)
- [validar_tabela_em_lotes_or](#funcao-37)
- [validar_tabela_em_lotes](#funcao-38)
- [anl_erro](#funcao-39)
- [limpar_texto_latin1](#funcao-40)
- [gerar_relatorio_erros](#funcao-41)
- [col](#funcao-42)
- [num](#funcao-43)
- [col](#funcao-44)
- [num](#funcao-45)
- [emitir](#funcao-46)
- [__new__](#funcao-47)
- [codigo](#funcao-48)
- [descricao](#funcao-49)
- [teste](#funcao-50)
- [descricao_por_codigo](#funcao-51)
- [_mapa](#funcao-52)
- [_codigos](#funcao-53)
- [teste](#funcao-54)
- [__new__](#funcao-55)
- [codigo](#funcao-56)
- [descricao](#funcao-57)
- [teste](#funcao-58)
- [descricao_por_codigo](#funcao-59)
- [_mapa](#funcao-60)
- [_codigos](#funcao-61)
- [__new__](#funcao-62)
- [codigo](#funcao-63)
- [descricao](#funcao-64)
- [teste](#funcao-65)
- [descricao_por_codigo](#funcao-66)
- [_mapa](#funcao-67)
- [_codigos](#funcao-68)
- [__new__](#funcao-69)
- [codigo](#funcao-70)
- [descricao](#funcao-71)
- [teste](#funcao-72)
- [descricao_por_codigo](#funcao-73)
- [_mapa](#funcao-74)
- [_codigos](#funcao-75)
- [__new__](#funcao-76)
- [codigo](#funcao-77)
- [descricao](#funcao-78)
- [teste](#funcao-79)
- [descricao_por_codigo](#funcao-80)
- [_mapa](#funcao-81)
- [_codigos](#funcao-82)
- [__init__](#funcao-83)
- [codigo](#funcao-84)
- [descricao](#funcao-85)
- [teste](#funcao-86)
- [descricao_por_codigo](#funcao-87)
- [_mapa](#funcao-88)
- [_codigos](#funcao-89)
- [__new__](#funcao-90)
- [codigo](#funcao-91)
- [descricao](#funcao-92)
- [teste](#funcao-93)
- [descricao_por_codigo](#funcao-94)
- [_mapa](#funcao-95)
- [_codigos](#funcao-96)
- [teste](#funcao-97)
- [testeQ5](#funcao-98)
- [__new__](#funcao-99)
- [codigo](#funcao-100)
- [descricao](#funcao-101)
- [teste](#funcao-102)
- [descricao_por_codigo](#funcao-103)
- [_mapa](#funcao-104)
- [_codigos](#funcao-105)
- [validar_datas](#funcao-106)
- [validar_data_opcional](#funcao-107)
- [validar_decimais_positivos](#funcao-108)
- [validar_decimais](#funcao-109)
- [validar_projeto_origem](#funcao-110)
- [validar_percentuais](#funcao-111)
- [validar_atributos](#funcao-112)
- [validar_flag](#funcao-113)
- [validar_tipo_oe](#funcao-114)
- [validar_inteiros_positivos](#funcao-115)
- [validar_aneel](#funcao-116)
- [validar_textos](#funcao-117)
- [validar_unidade](#funcao-118)
- [validar_uar](#funcao-119)
- [validar_codigos](#funcao-120)
- [validar_cc](#funcao-121)
- [validar_tuc](#funcao-122)
- [validar_ti](#funcao-123)
- [validar_ti_origem](#funcao-124)
- [capturar_erros_estrutura](#funcao-125)
- [pipeline_validacao_completa](#funcao-126)
- [_coletar_erros_estrutura](#funcao-127)
- [_executar_regras_negocio](#funcao-128)
- [_executar_regra](#funcao-129)
- [validar_TI](#funcao-130)
- [validar_cd](#funcao-131)
- [validar_vl](#funcao-132)
- [_decimal_br](#funcao-133)
- [validar_consistencia_valores](#funcao-134)
- [validar_ide](#funcao-135)
- [validar_ide1](#funcao-136)
- [validar_cd](#funcao-137)
- [validar_cda](#funcao-138)
- [validar_cdd](#funcao-139)
- [validar_txt](#funcao-140)
- [validar_Dt](#funcao-141)
- [validar_vl](#funcao-142)
- [validar_vl_pct](#funcao-143)
- [validar_tipo_obra](#funcao-144)
- [validar_nr_fas](#funcao-145)
- [validar_ide](#funcao-146)
- [validar_ide1](#funcao-147)
- [validar_cd](#funcao-148)
- [validar_cda](#funcao-149)
- [validar_cdd](#funcao-150)
- [validar_txt](#funcao-151)
- [validar_Dt](#funcao-152)
- [validar_vl](#funcao-153)
- [validar_vl_pct](#funcao-154)
- [validar_tipo_obra](#funcao-155)
- [validar_nr_fas](#funcao-156)
- [verifica_dados](#funcao-157)
- [validar_cds](#funcao-158)
- [validar_flg_dir](#funcao-159)
- [validar_vl_cda](#funcao-160)
- [validar_cnpj](#funcao-161)
- [validar_vl_cdng](#funcao-162)
- [validar_vl_cdca](#funcao-163)
- [validar_vl_voc](#funcao-164)
- [validar_TUC](#funcao-165)
- [validar_TI](#funcao-166)
- [validar_Dt](#funcao-167)
- [validar_nr_a1](#funcao-168)
- [validar_ide](#funcao-169)
- [validar_Txt_N](#funcao-170)
- [validar_und](#funcao-171)
- [validar_FLG](#funcao-172)
- [validar_FLGa](#funcao-173)
- [validar_cd](#funcao-174)
- [validar_cd1](#funcao-175)
- [validar_cd2](#funcao-176)
- [validar_cd21](#funcao-177)
- [validar_desc](#funcao-178)
- [verifica_dados](#funcao-179)
- [validar_vl_cda](#funcao-180)
- [validar_cnpj](#funcao-181)
- [validar_vl_cdng](#funcao-182)
- [validar_vl_cdca](#funcao-183)
- [validar_vl_voc](#funcao-184)
- [validar_TUC](#funcao-185)
- [validar_TI](#funcao-186)
- [validar_Dt](#funcao-187)
- [validar_nr_a1](#funcao-188)
- [validar_ide](#funcao-189)
- [validar_Txt_N](#funcao-190)
- [validar_und](#funcao-191)
- [validar_FLG](#funcao-192)
- [validar_FLGa](#funcao-193)
- [validar_cd](#funcao-194)
- [validar_cd1](#funcao-195)
- [validar_cd2](#funcao-196)
- [validar_cd21](#funcao-197)
- [validar_desc](#funcao-198)
- [validar_FLG](#funcao-199)
- [validar_cnpj](#funcao-200)
- [validar_vl_cdng](#funcao-201)
- [validar_vl_cdca](#funcao-202)
- [validar_vl_voc](#funcao-203)
- [validar_TUC](#funcao-204)
- [validar_TI](#funcao-205)
- [validar_Dt](#funcao-206)
- [validar_nr_a1](#funcao-207)
- [validar_ide](#funcao-208)
- [validar_Txt_N](#funcao-209)
- [validar_und](#funcao-210)
- [validar_cd](#funcao-211)
- [validar_cd2](#funcao-212)
- [validar_cd1](#funcao-213)
- [validar_desc](#funcao-214)
- [validar_cd](#funcao-215)
- [validar_txt](#funcao-216)
- [validar_cd](#funcao-217)
- [validar_desc](#funcao-218)
- [validar_depara](#funcao-219)
- [validar_FC](#funcao-220)
- [validar_FLG_AGR](#funcao-221)
- [validar_Cd_Nm](#funcao-222)
- [validar_Cd_Nm1](#funcao-223)
- [validar_FLG](#funcao-224)
- [validar_cd](#funcao-225)
- [validar_cd1](#funcao-226)
- [validar_Cd_Nm](#funcao-227)
- [validar_desc](#funcao-228)
- [validar_Cd_Nm1](#funcao-229)
- [validar_FC](#funcao-230)
- [validar_cd](#funcao-231)
- [validar_und](#funcao-232)
- [validar_fat](#funcao-233)
- [validar_Dt](#funcao-234)
- [validar_Hr](#funcao-235)
- [validar_cd3](#funcao-236)
- [validar_cd](#funcao-237)
- [validar_cd1](#funcao-238)
- [validar_cd2](#funcao-239)
- [validar_desc](#funcao-240)
- [validar_frini](#funcao-241)
- [validar_cnpj](#funcao-242)
- [validar_serie](#funcao-243)
- [validar_nr](#funcao-244)
- [validar_TI](#funcao-245)
- [validar_ide](#funcao-246)
- [validar_FLG](#funcao-247)
- [validar_und](#funcao-248)
- [validar_cd](#funcao-249)
- [validar_TUC](#funcao-250)
- [validar_nr_a1](#funcao-251)
- [validar_ide](#funcao-252)
- [validar_cd](#funcao-253)
- [validar_desc](#funcao-254)
- [validar_depara](#funcao-255)
- [validar_FC](#funcao-256)
- [validar_ide](#funcao-257)
- [validar_cd](#funcao-258)
- [validar_FLG](#funcao-259)
- [validar_nr_fas](#funcao-260)
- [validar_ide](#funcao-261)
- [validar_cd](#funcao-262)
- [validar_FLG](#funcao-263)
- [validar_ide](#funcao-264)
- [validar_cd](#funcao-265)
- [validar_us](#funcao-266)
- [validar_ano](#funcao-267)
- [validar_vl](#funcao-268)
- [validar_dt](#funcao-269)
- [validar_tp](#funcao-270)
- [validar_ide](#funcao-271)
- [validar_cd](#funcao-272)
- [validar_vls](#funcao-273)
- [validar_FLG](#funcao-274)
- [validar_ide](#funcao-275)
- [validar_cd](#funcao-276)
- [validar_us](#funcao-277)
- [validar_Dt](#funcao-278)
- [validar_ide](#funcao-279)
- [validar_cd](#funcao-280)
- [validar_us](#funcao-281)
- [validar_Dt](#funcao-282)
- [validar_ide](#funcao-283)
- [validar_cd](#funcao-284)
- [validar_us](#funcao-285)
- [validar_Dt](#funcao-286)
- [validar_ide](#funcao-287)
- [validar_cd](#funcao-288)
- [validar_vls](#funcao-289)
- [validar_ide](#funcao-290)
- [validar_cd](#funcao-291)
- [validar_vls](#funcao-292)
- [validar_ide](#funcao-293)
- [validar_cd](#funcao-294)
- [validar_vls](#funcao-295)
- [validar_ide](#funcao-296)
- [validar_cd](#funcao-297)
- [validar_vls](#funcao-298)
- [validar_ide](#funcao-299)
- [validar_cd](#funcao-300)
- [validar_vls](#funcao-301)
- [validar_ide](#funcao-302)
- [validar_cd](#funcao-303)
- [validar_vls](#funcao-304)
- [validar_ide](#funcao-305)
- [validar_cd](#funcao-306)
- [validar_vls](#funcao-307)
- [validar_ide](#funcao-308)
- [validar_cd](#funcao-309)
- [validar_vls](#funcao-310)
- [validar_ide](#funcao-311)
- [validar_cd](#funcao-312)
- [validar_cstipi](#funcao-313)
- [validar_csticms](#funcao-314)
- [validar_cdp](#funcao-315)
- [validar_txt](#funcao-316)
- [validar_FLG](#funcao-317)
- [validar_vl](#funcao-318)
- [validar_vl_odc](#funcao-319)
- [validar_al](#funcao-320)
- [validar_Dt](#funcao-321)
- [validar_vl_cdng](#funcao-322)
- [validar_und](#funcao-323)
- [validar_cfop](#funcao-324)
- [validar_ncm](#funcao-325)
- [validar_extipi](#funcao-326)
- [validar_cnpk](#funcao-327)
- [validar_serie](#funcao-328)
- [validar_nr](#funcao-329)
- [validar_NFe](#funcao-330)
- [verifica_dados](#funcao-331)
- [_erro](#funcao-332)
- [_texto](#funcao-333)
- [_valor](#funcao-334)
- [_normalizar_numero](#funcao-335)
- [_validar_cfop](#funcao-336)
- [_validar_chave_nfe](#funcao-337)
- [_validar_flags](#funcao-338)
- [_validar_ipi](#funcao-339)
- [_validar_icms](#funcao-340)
- [_validar_valores](#funcao-341)
- [_validar_aliquotas](#funcao-342)
- [validar_ide](#funcao-343)
- [validar_txt](#funcao-344)
- [validar_txt1](#funcao-345)
- [validar_vl](#funcao-346)
- [validar_Dt](#funcao-347)
- [validar_nr_a1](#funcao-348)
- [validar_TUC](#funcao-349)
- [validar_ide](#funcao-350)
- [validar_ITEM](#funcao-351)
- [validar_ITEM1](#funcao-352)
- [validar_txt](#funcao-353)
- [validar_NRform](#funcao-354)
- [validar_vl](#funcao-355)
- [validar_TUC](#funcao-356)
- [validar_ide](#funcao-357)
- [validar_ITEM](#funcao-358)
- [validar_FLG](#funcao-359)
- [validar_Dt](#funcao-360)
- [validar_Dtr](#funcao-361)
- [validar_nr_a1](#funcao-362)
- [validar_TUC](#funcao-363)
- [validar_ide](#funcao-364)
- [validar_ide1](#funcao-365)
- [validar_txt](#funcao-366)
- [validar_cd](#funcao-367)
- [validar_cdop](#funcao-368)
- [validar_NRform](#funcao-369)
- [validar_vl](#funcao-370)
- [validar_ide](#funcao-371)
- [validar_txt](#funcao-372)
- [validar_txt1](#funcao-373)
- [validar_vl](#funcao-374)
- [validar_Dt](#funcao-375)
- [validar_al](#funcao-376)
- [validar_vl_cdng](#funcao-377)
- [validar_und](#funcao-378)
- [validar_cnpj](#funcao-379)
- [validar_serie](#funcao-380)
- [validar_nr](#funcao-381)
- [validar_NFe](#funcao-382)
- [validar_FLG](#funcao-383)
- [validar_TPFAT](#funcao-384)
- [validar_cd](#funcao-385)
- [validar_cd1](#funcao-386)
- [verifica_dados](#funcao-387)
- [validar_ide](#funcao-388)
- [validar_ide1](#funcao-389)
- [validar_txt](#funcao-390)
- [validar_txt1](#funcao-391)
- [validar_cd](#funcao-392)
- [validar_ide2](#funcao-393)
- [validar_vl](#funcao-394)
- [validar_nr_a1](#funcao-395)
- [validar_TUC](#funcao-396)
- [validar_UAR](#funcao-397)
- [validar_ide1](#funcao-398)
- [validar_FLG](#funcao-399)
- [validar_cds](#funcao-400)
- [validar_cds1](#funcao-401)
- [validar_dig_inc](#funcao-402)
- [validar_Dt](#funcao-403)
- [validar_TI](#funcao-404)
- [validar_TUC](#funcao-405)
- [validar_nr_a1](#funcao-406)
- [validar_ide](#funcao-407)
- [validar_txt](#funcao-408)
- [validar_NRform](#funcao-409)
- [validar_vl](#funcao-410)
- [verifica_dados](#funcao-411)
- [validar_cds](#funcao-412)
- [validar_txt](#funcao-413)
- [validar_ide](#funcao-414)
- [validar_cd](#funcao-415)
- [validar_Dt](#funcao-416)
- [validar_FLG](#funcao-417)
- [validar_ide3](#funcao-418)
- [validar_ide2](#funcao-419)
- [validar_ide](#funcao-420)
- [validar_ide1](#funcao-421)
- [validar_ideais](#funcao-422)
- [validar_TI](#funcao-423)
- [validar_TUC](#funcao-424)
- [validar_nr_a1](#funcao-425)
- [validar_txt](#funcao-426)
- [validar_cds](#funcao-427)
- [validar_cds1](#funcao-428)
- [validar_dig_inc](#funcao-429)
- [validar_CC](#funcao-430)
- [validar_UAR](#funcao-431)
- [validar_NRform](#funcao-432)
- [validar_vl](#funcao-433)
- [verifica_dados](#funcao-434)
- [validar_Dt](#funcao-435)
- [validar_FLG](#funcao-436)
- [validar_ide](#funcao-437)
- [validar_ide1](#funcao-438)
- [validar_ideais](#funcao-439)
- [validar_vl](#funcao-440)
- [validar_vl_pct_ori](#funcao-441)
- [validar_ide2](#funcao-442)
- [verifica_dados](#funcao-443)
- [validar_ide2a](#funcao-444)
- [validar_vl_pct_ori](#funcao-445)
- [validar_ide](#funcao-446)
- [validar_cd](#funcao-447)
- [validar_cdx](#funcao-448)
- [validar_Dt](#funcao-449)
- [validar_Dt1](#funcao-450)
- [validar_FLG](#funcao-451)
- [validar_ide1](#funcao-452)
- [validar_ide2](#funcao-453)
- [validar_ide3](#funcao-454)
- [validar_ideais](#funcao-455)
- [validar_TI](#funcao-456)
- [validar_TUC](#funcao-457)
- [validar_nr_a1](#funcao-458)
- [validar_txt](#funcao-459)
- [validar_sisbase](#funcao-460)
- [validar_cds](#funcao-461)
- [validar_dig_inc](#funcao-462)
- [validar_CC](#funcao-463)
- [validar_UAR](#funcao-464)
- [validar_UNID](#funcao-465)
- [validar_vl](#funcao-466)
- [validar_regras_de_dominio](#funcao-467)
- [validar_cd](#funcao-468)
- [validar_Dt](#funcao-469)
- [validar_FLG](#funcao-470)
- [validar_ide](#funcao-471)
- [validar_txt](#funcao-472)
- [validar_CC](#funcao-473)
- [validar_UNID](#funcao-474)
- [validar_vl](#funcao-475)
- [validar_ide](#funcao-476)
- [validar_Dt](#funcao-477)
- [validar_CC](#funcao-478)
- [validar_UNID](#funcao-479)
- [validar_ide](#funcao-480)
- [validar_TUC](#funcao-481)
- [validar_CC](#funcao-482)
- [validar_UNID](#funcao-483)
- [validar_cd](#funcao-484)
- [validar_UNID](#funcao-485)
- [validar_vl](#funcao-486)
- [validar_CC](#funcao-487)
- [validar_UNID](#funcao-488)
- [validar_ide](#funcao-489)
- [validar_IND](#funcao-490)
- [validar_Dt](#funcao-491)
- [validar_vl](#funcao-492)
- [validar_CC](#funcao-493)
- [validar_ide](#funcao-494)
- [validar_IND](#funcao-495)
- [validar_Dt](#funcao-496)
- [validar_vl](#funcao-497)
- [validar_hist](#funcao-498)
- [validar_CC](#funcao-499)
- [validar_UNID](#funcao-500)
- [validar_NUM](#funcao-501)
- [validar_ide](#funcao-502)
- [validar_IND](#funcao-503)
- [validar_vl](#funcao-504)
- [validar_CC](#funcao-505)
- [validar_ide](#funcao-506)
- [validar_Dt](#funcao-507)
- [validar_TI](#funcao-508)
- [validar_cds](#funcao-509)
- [validar_vl_cdng](#funcao-510)
- [validar_vl_tpajst](#funcao-511)
- [validar_vl](#funcao-512)
- [validar_datas](#funcao-513)
- [validar_vl_voc](#funcao-514)
- [valida_nr_ax](#funcao-515)
- [validar_dig_inc](#funcao-516)
- [validar_ide](#funcao-517)
- [valida_textos](#funcao-518)
- [validar_UND](#funcao-519)
- [validar_UAR](#funcao-520)
- [validar_cds](#funcao-521)
- [validar_TUC](#funcao-522)
- [validar_TI](#funcao-523)
- [validar_vl_tpajst](#funcao-524)
- [silenciador_de_erros](#funcao-525)
- [pipeline_validacao_completa](#funcao-526)
- [validar_datas](#funcao-527)
- [validar_valores_e_horas](#funcao-528)
- [validar_ide](#funcao-529)
- [valida_txt_ativ_exec](#funcao-530)
- [valida_txt_obs](#funcao-531)
- [valida_dsc_cargo](#funcao-532)
- [validar_campos_texto_25](#funcao-533)
- [validar_cod_ccus](#funcao-534)
- [validar_ind_fl](#funcao-535)
- [silenciador_de_erros](#funcao-536)
- [erros](#funcao-537)
- [validar_vl_rubr](#funcao-538)
- [validar_ide](#funcao-539)
- [validar_cod_rubrica](#funcao-540)
- [validar_ind_rubr](#funcao-541)
- [silenciador_de_erros](#funcao-542)
- [validar_tabela](#funcao-543)
- [validar_vl_rubr](#funcao-544)
- [validar_ide](#funcao-545)
- [validar_cod_rubrica](#funcao-546)
- [validar_ind_rubr](#funcao-547)
- [silenciador_de_erros](#funcao-548)
- [validar_tabela](#funcao-549)
- [validar_datas](#funcao-550)
- [validar_vl_rubr](#funcao-551)
- [validar_ide](#funcao-552)
- [validar_cod_rubrica](#funcao-553)
- [validar_ind_rubr](#funcao-554)
- [validar_text](#funcao-555)
- [validar_text1](#funcao-556)
- [validar_text2](#funcao-557)
- [silenciador_de_erros](#funcao-558)
- [validar_tabela](#funcao-559)
- [validar_datas](#funcao-560)
- [validar_vl_rubr](#funcao-561)
- [validar_ide](#funcao-562)
- [validar_cod_rubrica](#funcao-563)
- [validar_ind_rubr](#funcao-564)
- [silenciador_de_erros](#funcao-565)
- [validar_tabela](#funcao-566)
- [adicionar](#funcao-567)
- [to_date](#funcao-568)
- [obter](#funcao-569)
- [esta_vazio](#funcao-570)
- [adicionar_erro](#funcao-571)
- [converter_decimal](#funcao-572)
- [texto](#funcao-573)
- [validar_tp_bem](#funcao-574)
- [validar_voc_ca_avaliacao_2](#funcao-575)
- [validar_pct_oe](#funcao-576)
- [executar](#funcao-577)
- [check](#funcao-578)
- [erro](#funcao-579)
- [dec](#funcao-580)
- [soma_igual](#funcao-581)

---

<a id="funcao-1"></a>

## referencias_incr

Lê e processa arquivos CSV para obter conjuntos de referências incrementais.

A função lê três arquivos CSV (TBL_TUC_INFRA.csv, TBL_TUC_ORC.csv e IPCA.csv) a partir de uma pasta especificada. Processa esses dados para criar conjuntos de referências incrementais e retorna esses conjuntos juntamente com um DataFrame contendo os índices IPCA válidos.

### Assinatura

```python
def referencias_incr(pasta='tabelas'):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pasta` | `str` | Caminho para a pasta onde estão armazenados os arquivos CSV. O valor padrão é 'tabelas'. |

### Retorno

**Tipo:** `tuple[set[str], set[tuple[str, str]], set[str], pd.DataFrame]`

Um tuple contendo quatro elementos: dois conjuntos de referências incrementais (infra0 e infrapar) e dois conjuntos de referências incrementais (orca0). O último elemento é um DataFrame com os índices IPCA válidos.

### Exceções

- **`ValueError`**: Quando a tabela IPCA não contém datas e índices válidos.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def referencias_incr(pasta='tabelas'):
    pasta = Path(pasta)
    infra = pd.read_csv(pasta / 'TBL_TUC_INFRA.csv', sep='|', encoding='latin-1', dtype=str,
                        usecols=['Nr_TUC', 'Nr_A1']).fillna('')
    orca = pd.read_csv(pasta / 'TBL_TUC_ORC.csv', sep='|', encoding='latin-1', dtype=str,
                       usecols=['Nr_TUC', 'Nr_A1']).fillna('')
    ipca = pd.read_csv(pasta / 'IPCA.csv', sep='|', encoding='latin-1',
                       usecols=['Dt_REF', 'Nr_IPCA'], dtype=str)
    ipca['Dt_REF'] = pd.to_datetime(ipca['Dt_REF'], format="%Y-%m-%d", errors='coerce', dayfirst=True)
    ipca['Nr_IPCA'] = pd.to_numeric(ipca['Nr_IPCA'].str.replace(',', '.', regex=False), errors='coerce')
    ipca = (ipca.dropna(subset=['Dt_REF', 'Nr_IPCA'])
                .sort_values('Dt_REF').drop_duplicates('Dt_REF', keep='last'))
    if ipca.empty:
        raise ValueError('Tabela IPCA não contém datas e índices válidos')
    infra0 = set(infra.loc[infra['Nr_A1'].eq('0'), 'Nr_TUC'])
    infrapar = set(map(tuple, infra.loc[infra['Nr_A1'].ne('0'), ['Nr_TUC', 'Nr_A1']].to_numpy()))
    orca0 = set(orca.loc[orca['Nr_A1'].eq('0'), 'Nr_TUC'])
    return infra0, infrapar, orca0, ipca
```

</details>

---

<a id="funcao-2"></a>

## gravar_agregado_incr

Grava um agregado incremental de dados em um arquivo Parquet.

A função processa uma base de dados, filtrando e agrupando os dados conforme especificações, e então grava o resultado em um arquivo Parquet. O nome do arquivo é gerado com base no número do lote fornecido.

### Assinatura

```python
# Consulte o código-fonte de gravar_agregado_incr
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `base_agregada` | `pd.DataFrame` | Base de dados a ser processada. |
| `nr_lote` | `int` | Número do lote, usado para nomear o arquivo de saída. |
| `pasta` | `str` | Caminho da pasta onde o arquivo será gravado. A pasta é criada se não existir. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Dependências

- `{'nome': 'numpy', 'categoria': 'import'}`
- `{'nome': 'pandas', 'categoria': 'import'}`
- `{'nome': 'pathlib.Path', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gravar_agregado_incr(
                            base_agregada: pd.DataFrame,
                            nr_lote: int,
                            pasta: str = "tabelas/agregados_incr"
                        ) -> None:

    destino = Path(pasta)
    destino.mkdir(parents=True, exist_ok=True)

    colunas = [
                    "Nr_TI",
                    "Nr_TUC",
                    "Cd_TP_AVAL",
                    "COD_ITEM",
                    "VOC_ATUALIZADO",
                    "VOC_VF_ATUALIZADO",
                    "VNR",
                    "VNR_VF_TOTAL",
                    "Qtd_AIS"
                ]

    df = base_agregada[colunas].copy()

    for campo in ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL","COD_ITEM"]:
        df[campo] = df[campo].astype("string").str.strip()

    for campo in ["VOC_ATUALIZADO", "VNR", "VNR_VF_TOTAL", "VOC_VF_ATUALIZADO", "Qtd_AIS"]:
        df[campo] = pd.to_numeric(df[campo], errors="coerce")

    df = df.loc[
                    df["Cd_TP_AVAL"].isin(["1", "2"])
                    & df["Nr_TI"].notna()
                    & df["Nr_TUC"].notna()
                    & df["Nr_TI"].ne("")
                    & df["Nr_TUC"].ne("")
                    & np.isfinite(df["VOC_ATUALIZADO"])
                    & np.isfinite(df["VNR"])
                    & df["VOC_ATUALIZADO"].gt(0)
                    & df["VNR"].ge(0)
                ]

    agregado = (
                    df.groupby(
                        ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL", "COD_ITEM"],
                        as_index=False
                    )
                    .agg(
                        VOCa=("VOC_ATUALIZADO", "sum"),
                        VNR=("VNR", "sum"),
                        Qtd_Registros=("VNR", "size"),
                        VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                        VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                        Qtd_AIS=("Qtd_AIS", "sum"),
                    )
                )

    arquivo = destino / f"INCR_agregado_lote_{nr_lote:06d}.parquet"
    temporario = destino / f"INCR_agregado_lote_{nr_lote:06d}.tmp.parquet"

    agregado.to_parquet(temporario, index=False)
    temporario.replace(arquivo)
```

</details>

---

<a id="funcao-3"></a>

## consolidar_agregados_incr

Consolida agregados incrementais de arquivos Parquet em um DataFrame Pandas.

A função lê arquivos Parquet que correspondem ao padrão 'INCR_agregado_lote_*.parquet' na pasta especificada, agrupa os dados por várias colunas e realiza a soma dos valores para as colunas indicadas. Se não houver arquivos na pasta, retorna um DataFrame vazio.

### Assinatura

```python
# Consulte o código-fonte de consolidar_agregados_incr
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `pasta` | `str` | Caminho para a pasta contendo os arquivos Parquet a serem consolidados. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame Pandas com os dados consolidados e agregados.

### Dependências

- `{'nome': 'glob', 'categoria': 'import'}`
- `{'nome': 'pandas', 'categoria': 'import'}`
- `{'nome': 'pathlib.Path', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def consolidar_agregados_incr(
                                pasta: str = "tabelas/agregados_incr"
                            ) -> pd.DataFrame:

    arquivos = sorted(
                        Path(pasta).glob("INCR_agregado_lote_*.parquet")
                    )

    if not arquivos:
        return pd.DataFrame()

    parciais = [
                    pd.read_parquet(arquivo)
                    for arquivo in arquivos
                ]

    df = pd.concat(parciais, ignore_index=True)

    return (
                df.groupby(
                    ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL", "COD_ITEM"],
                    as_index=False
                )
                .agg(
                    VOCa=("VOCa", "sum"),
                    VNR=("VNR", "sum"),
                    Qtd_Registros=("Qtd_Registros", "sum"),
                    VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                    VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                    Qtd_AIS=("Qtd_AIS", "sum")
                )
            )
```

</details>

---

<a id="funcao-4"></a>

## analisar_vf_agregado_incr

Analisa um DataFrame consolidado para calcular métricas de valor agregado incrementado.

A função agrupa o DataFrame consolidado por diferentes níveis e calcula métricas como soma de valores, quantidade de itens e unidades. Filtra os resultados com base em condições específicas e retorna um novo DataFrame com as métricas calculadas.

### Assinatura

```python
def analisar_vf_agregado_incr(consolidado: pd.DataFrame) -> pd.DataFrame:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `consolidado` | `pd.DataFrame` | DataFrame consolidado contendo dados a serem analisados. |

### Retorno

**Tipo:** `pd.DataFrame`

Novo DataFrame com as métricas calculadas e filtradas.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def analisar_vf_agregado_incr(consolidado: pd.DataFrame) -> pd.DataFrame:

    niveis = {
                "TI/TUC/COD_ITEM": ["Nr_TI", "Nr_TUC", "COD_ITEM", "Cd_TP_AVAL"],
                "TI/COD_ITEM": ["Nr_TI", "COD_ITEM", "Cd_TP_AVAL"],
                "TUC/COD_ITEM": ["Nr_TUC", "COD_ITEM", "Cd_TP_AVAL"],
                "COD_ITEM": ["COD_ITEM", "Cd_TP_AVAL"],            
            }

    resultados = []

    for nivel, chaves in niveis.items():

        df = (
                consolidado
                .groupby(chaves, as_index=False, dropna=False)
                .agg(
                    VOC_VF_ATUALIZADO=("VOC_VF_ATUALIZADO", "sum"),
                    VNR_VF_TOTAL=("VNR_VF_TOTAL", "sum"),
                    Qtd_AIS=("Qtd_AIS", "sum"),
                )
            )

        df = df.loc[df["Qtd_AIS"].gt(0)].copy()

        df["VOC_VF_UNIT_ATUALIZADO"] = (
                                            df["VOC_VF_ATUALIZADO"] / df["Qtd_AIS"]
                                        )

        df["VNR_VF_UNIT"] = (
                                df["VNR_VF_TOTAL"] / df["Qtd_AIS"]
                            )

        df = df.loc[df["VOC_VF_UNIT_ATUALIZADO"].gt(0)].copy()

        df["Diferenca_Pct"] = (
                                    df["VNR_VF_UNIT"] / df["VOC_VF_UNIT_ATUALIZADO"] - 1
                                ) * 100

        df["Limite_Pct"] = 15.0

        df = df.loc[df["Diferenca_Pct"].abs().gt(15)].copy()

        if df.empty:
            continue

        df["Nivel"] = nivel
        df["Nr_TI"] = df.get("Nr_TI", pd.NA)
        df["Nr_TUC"] = df.get("Nr_TUC", pd.NA)
        df["COD_ITEM"] = df.get("COD_ITEM", pd.NA)

        resultados.append(df)

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados, ignore_index=True)
```

</details>

---

<a id="funcao-5"></a>

## analisar_agregados_incr

Analisa agregados incrementais em um DataFrame consolidado.

A função agrupa os dados do DataFrame consolidado por diferentes níveis e calcula métricas como VOCa, VNR e Qtd_Registros. Filtra os resultados com base em uma diferença percentual e um limite percentual específico para cada nível de agregação.

### Assinatura

```python
# Consulte o código-fonte de analisar_agregados_incr
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `consolidado` | `pd.DataFrame` | DataFrame consolidado contendo as colunas 'VOCa', 'VNR', 'Qtd_Registros', 'Nr_TI', 'Nr_TUC' e 'Cd_TP_AVAL'. |

### Retorno

**Tipo:** `pd.DataFrame`

DataFrame resultante com os resultados filtrados e agregados por nível.

### Dependências

- `numpy`
- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def analisar_agregados_incr(
                                consolidado: pd.DataFrame
                            ) -> pd.DataFrame:

    if consolidado.empty:
        return pd.DataFrame()

    niveis = {
                "TI/TUC": ["Nr_TI", "Nr_TUC", "Cd_TP_AVAL"],
                "TI": ["Nr_TI", "Cd_TP_AVAL"],
                "TUC": ["Nr_TUC", "Cd_TP_AVAL"],
                "TP_AVAL": ["Cd_TP_AVAL"]
            }

    resultados = []

    for nivel, chaves in niveis.items():

        df = (
                    consolidado.groupby(
                        chaves,
                        as_index=False
                    )
                    .agg(
                        VOCa=("VOCa", "sum"),
                        VNR=("VNR", "sum"),
                        Qtd_Registros=("Qtd_Registros", "sum")
                    )
                )

        df = df.loc[df["VOCa"].gt(0)].copy()

        df["Diferenca_Pct"] = (
                                    (df["VNR"] / df["VOCa"]) - 1
                                ) * 100

        df["Limite_Pct"] = np.where(
                                        df["Cd_TP_AVAL"].eq("2"),
                                        5.0,
                                        2.0
                                    )

        df = df.loc[
                        df["Diferenca_Pct"].abs() > df["Limite_Pct"]
                    ].copy()

        if df.empty:
            continue

        df["Nivel"] = nivel

        if "Nr_TI" not in df.columns:
            df["Nr_TI"] = pd.NA

        if "Nr_TUC" not in df.columns:
            df["Nr_TUC"] = pd.NA

        resultados.append(df)

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados, ignore_index=True)
```

</details>

---

<a id="funcao-6"></a>

## gerar_alertas_incr_vf_agregados

Gera alertas com base em divergências entre valores agregados e valores unitários.

A função processa um DataFrame contendo divergências e gera uma lista de dicionários, cada um representando um alerta. Os alertas são gerados para registros que apresentam diferenças percentuais significativas em relação aos valores unitários atualizados pelo IPCA.

### Assinatura

```python
# Consulte o código-fonte de gerar_alertas_incr_vf_agregados
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `divergencias` | `pd.DataFrame` | DataFrame contendo as divergências entre os valores agregados e os valores unitários. |

### Retorno

**Tipo:** `list[dict]`

Lista de dicionários, cada um representando um alerta com detalhes sobre a divergência encontrada.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_alertas_incr_vf_agregados(
                                    divergencias: pd.DataFrame
                                ) -> list[dict]:

    erros = []

    if divergencias.empty:
        return erros

    for registro in divergencias.itertuples(index=False):

        identificacao = []

        if pd.notna(registro.Nr_TI):
            identificacao.append(f"Nr_TI={registro.Nr_TI}")

        if pd.notna(registro.Nr_TUC):
            identificacao.append(f"Nr_TUC={registro.Nr_TUC}")

        if pd.notna(registro.COD_ITEM):
            identificacao.append(f"COD_ITEM={registro.COD_ITEM}")

        diferenca = float(registro.Diferenca_Pct)
        sentido = "acima" if diferenca > 0 else "abaixo"

        mensagem = (
                        f"Agregação {registro.Nivel}: "
                        f"{', '.join(identificacao)}; "
                        f"Cd_TP_AVAL={registro.Cd_TP_AVAL}; "
                        f"VNR VF unitário {abs(diferenca):,.2f}% {sentido} "
                        f"do VOC VF unitário atualizado pelo IPCA; "
                        f"tolerância ±15% "
                    ).replace(",","@").replace(".",",").replace("@",".")

        erros.append({
                        "type": "value_error",
                        "severidade": "ALERTA",
                        "loc": ("tabela", 0, "VL_VNR_UC"),
                        "msg": f"Alerta: {mensagem}",
                        "input": None,
                        "ctx": {"error": ValueError(mensagem)},
                        "etapa": 0,
                        "nivel_agregacao": registro.Nivel,
                        "Nr_TI": registro.Nr_TI,
                        "Nr_TUC": registro.Nr_TUC,
                        "diferenca_pct": round(diferenca, 2)
                    })

    return erros
```

</details>

---

<a id="funcao-7"></a>

## gerar_alertas_incr_agregados

Gera alertas incrementais agregados com base em divergências de dados.

A função processa um DataFrame contendo divergências e gera uma lista de dicionários representando alertas. Cada alerta inclui detalhes sobre a identificação do registro, o tipo de erro, a severidade, a localização, a mensagem de erro e informações adicionais.

### Assinatura

```python
# Consulte o código-fonte de gerar_alertas_incr_agregados
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `divergencias` | `pd.DataFrame` | DataFrame contendo as divergências que serão processadas para geração de alertas. |

### Retorno

**Tipo:** `list[dict]`

Lista de dicionários, onde cada dicionário representa um alerta com detalhes específicos.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_alertas_incr_agregados(
                                    divergencias: pd.DataFrame
                                ) -> list[dict]:

    erros = []

    if divergencias.empty:
        return erros

    for registro in divergencias.itertuples(index=False):

        identificacao = []

        if pd.notna(registro.Nr_TI):
            identificacao.append(f"Nr_TI={registro.Nr_TI}")

        if pd.notna(registro.Nr_TUC):
            identificacao.append(f"Nr_TUC={registro.Nr_TUC}")

        diferenca = float(registro.Diferenca_Pct)
        sentido = "acima" if diferenca > 0 else "abaixo"

        mensagem = (
                        f"Agregação {registro.Nivel}: "
                        f"{', '.join(identificacao)}; "
                        f"Cd_TP_AVAL={registro.Cd_TP_AVAL}; "
                        f"VNR {abs(diferenca):,.2f}% {sentido} "
                        f"do VOC atualizado pelo IPCA; "
                        f"tolerância ±{registro.Limite_Pct:.0f}%; "
                        f"{registro.Qtd_Registros} registros"
                    ).replace(",","@").replace(".",",").replace("@",".")

        erros.append({
                        "type": "value_error",
                        "severidade": "ALERTA",
                        "loc": ("tabela", 0, "VL_VNR_UC"),
                        "msg": f"Alerta: {mensagem}",
                        "input": None,
                        "ctx": {"error": ValueError(mensagem)},
                        "etapa": 0,
                        "nivel_agregacao": registro.Nivel,
                        "Nr_TI": registro.Nr_TI,
                        "Nr_TUC": registro.Nr_TUC,
                        "diferenca_pct": round(diferenca, 2)
                    })

    return erros
```

</details>

---

<a id="funcao-8"></a>

## validar_vnr_voc_ipca

Valida e processa dados de VNR, VOC e IPCA.

Esta função valida os dados fornecidos em um DataFrame `x` e um DataFrame `ipca`, aplicando deslocamentos temporais e calculando valores atualizados com base nos índices de IPCA. Retorna uma lista de dicionários contendo os dados validados e processados.

### Assinatura

```python
# Consulte o código-fonte de validar_vnr_voc_ipca
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `x` | `pd.DataFrame` | DataFrame contendo os dados a serem validados e processados. |
| `ipca` | `pd.DataFrame` | DataFrame contendo os índices de IPCA necessários para o cálculo dos valores atualizados. |
| `deslocamento` | `int` | Deslocamento temporal em meses a ser aplicado aos períodos de referência e início. |

### Retorno

**Tipo:** `list[dict]`

Lista de dicionários contendo os dados validados e processados.

### Dependências

- `numpy`
- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vnr_voc_ipca(
                            x: pd.DataFrame,
                            ipca: pd.DataFrame,
                            deslocamento: int = 0
                        ) -> list[dict]:

    erros = []

    def col(nome):
        return x[nome].astype("string").fillna("").str.strip()

    def num(nome):
        return pd.to_numeric(
                                col(nome).str.replace(",", ".", regex=False),
                                errors="coerce"
                            )

    tipo = col("Cd_TP_AVAL")
    voc = num("VL_VOC")
    vnr = num("VL_VNR_UC")
    voc_vf = num("VL_VOC_VF")

    dt_imob = (
                    pd.to_datetime(
                        col("Dt_Imob"),
                        format="%Y/%m/%d",
                        errors="coerce"
                    )
                    .dt.to_period("M")
                    .dt.to_timestamp(how="start")
                )

    dt_ref = (
                pd.to_datetime(
                    col("Dt_REF_DADOS"),
                    format="%Y/%m/%d",
                    errors="coerce"
                )
                .dt.to_period("M")
                .dt.to_timestamp(how="start")
            )

    elegiveis = (
                    tipo.isin(["1", "2"])
                    & voc.gt(0)
                    & vnr.notna()
                    & dt_imob.notna()
                    & dt_ref.notna()
                    & dt_ref.ge(dt_imob)
                )

    ids = np.flatnonzero(elegiveis.to_numpy(dtype=bool))

    if not len(ids):
        return erros

    base = pd.DataFrame({
                            "idx": ids,
                            "ini": dt_imob.iloc[ids].dt.to_period("M").dt.to_timestamp().to_numpy(),
                            "ref": dt_ref.iloc[ids].dt.to_period("M").dt.to_timestamp().to_numpy()
                        })

    tabela = ipca[["Dt_REF", "Nr_IPCA"]].copy()
    tabela = tabela.dropna(subset=["Dt_REF"])

    if tabela.empty:
        return erros

    ini = base[["idx", "ini"]].merge(
                                        tabela.rename(columns={"Dt_REF": "ini", "Nr_IPCA": "ipca_ini"}),
                                        on="ini",
                                        how="left",
                                        validate="many_to_one"
                                    )

    ref = base[["idx", "ref"]].merge(
                                        tabela.rename(columns={"Dt_REF": "ref", "Nr_IPCA": "ipca_ref"}),
                                        on="ref",
                                        how="left",
                                        validate="many_to_one"
                                    )

    fatores = ini[["idx", "ipca_ini"]].merge(
                                                ref[["idx", "ipca_ref"]],
                                                on="idx",
                                                how="inner",
                                                validate="one_to_one"
                                            )

    validos = (
                    fatores["ipca_ini"].gt(0)
                    & fatores["ipca_ref"].gt(0)
                )

    fatores = fatores.loc[validos]

    if fatores.empty:
        return erros

    idx = fatores["idx"].to_numpy(dtype=int)

    voc_atualizado = (
                        voc.iloc[idx].to_numpy(dtype=float)
                        * fatores["ipca_ref"].to_numpy(dtype=float)
                        / fatores["ipca_ini"].to_numpy(dtype=float)
                    )

    voc_vf_atualizado = (
                            voc_vf.iloc[idx].to_numpy(dtype=float)
                            * fatores["ipca_ref"].to_numpy(dtype=float)
                            / fatores["ipca_ini"].to_numpy(dtype=float)
                        )

    vnr_valores = vnr.iloc[idx].to_numpy(dtype=float)
    vnr_vf_valores = (num("VL_VNR_VF_UNIT").iloc[idx].to_numpy()
                      * num("Qtd_AIS").iloc[idx].to_numpy())

    base_agregada = pd.DataFrame({
                                    "idx": idx,
                                    "Nr_TI": col("Nr_TI").iloc[idx].to_numpy(),
                                    "Nr_TUC": col("Nr_TUC").iloc[idx].to_numpy(),
                                    "COD_ITEM": col("COD_ITEM").iloc[idx].to_numpy(),
                                    "Cd_TP_AVAL": tipo.iloc[idx].to_numpy(),
                                    "VOC_ATUALIZADO": voc_atualizado,
                                    "VOC_VF_ATUALIZADO": voc_vf_atualizado,
                                    "VNR": vnr_valores,
                                    "VNR_VF_TOTAL": vnr_vf_valores,
                                    "Qtd_AIS": num("Qtd_AIS").iloc[idx].to_numpy()
                                })
    base_agregada = base_agregada.loc[
                                        np.isfinite(base_agregada["VOC_ATUALIZADO"])
                                        & np.isfinite(base_agregada["VNR"])
                                        & base_agregada["VOC_ATUALIZADO"].gt(0)
                                        & base_agregada["VNR"].ge(0)
                                    ]
    
    return base_agregada
```

</details>

---

<a id="funcao-9"></a>

## validar_incr_bloco

Valida um DataFrame de acordo com regras específicas e retorna uma lista de erros encontrados.

A função valida um DataFrame contendo dados de avaliação, verificando várias condições e emitindo erros quando as regras não são atendidas. As verificações incluem tipos de avaliação, valores numéricos, datas e consistência entre campos.

### Assinatura

```python
# Consulte o código-fonte de validar_incr_bloco
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `df` | `pd.DataFrame` | DataFrame contendo os dados a serem validados. |
| `deslocamento` | `int` | Deslocamento para identificar a etapa de validação. |
| `pasta` | `Não especificado` | Pasta onde estão armazenadas as referências necessárias para a validação. |
| `dt_fim` | `Não especificado` | Data final do trabalho, usada para verificar se a data de referência é posterior a essa data. |

### Retorno

**Tipo:** `list[dict]`

Lista de dicionários contendo informações sobre os erros encontrados durante a validação.

### Dependências

- `{'nome': 'numpy', 'categoria': 'import'}`
- `{'nome': 'pandas', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_incr_bloco(df: pd.DataFrame, deslocamento: int = 0,
                        pasta='tabelas', dt_fim=None) -> list[dict]:

    if df.empty:
        return []

    x = df.reset_index(drop=True)
    n = len(x)
    erros = []

    def col(nome):
        if nome not in x.columns:
            return pd.Series('', index=x.index, dtype='string')
        return x[nome].astype('string').fillna('').str.strip()

    def num(nome):
        return pd.to_numeric(col(nome).str.replace(',', '.', regex=False), errors='coerce')

    def emitir(mascara, campo, mensagem):
        if isinstance(mascara, pd.Series):
            indices = np.flatnonzero(mascara.fillna(False).to_numpy(dtype=bool))
        else:
            indices = np.flatnonzero(np.asarray(mascara, dtype=bool))
        for i in indices:
            erros.append({
                            'type': 'value_error',
                            'loc': ('tabela', int(i), campo),
                            'msg': f'Value error, {mensagem}',
                            'input': x.at[int(i), campo] if campo in x else None,
                            'ctx': {'error': ValueError(mensagem)},
                            'etapa': deslocamento,
                        })

    tipo = col('Cd_TP_AVAL')
    tuc = col('Nr_TUC')
    a1 = col('Nr_A1')
    sis = col('Cd_SISBASE')
    oat = col('FLG_OAT')
    elg = col("FLG_ELIG")
    conc = col("Cd_CONC")

    emitir(tipo.eq('2') & (sis.eq('') | sis.eq('NA')) & elg.eq('1') & conc.isin(['1', '3']),
           'Cd_SISBASE', 'Cd_SISBASE obrigatório quando Cd_TP_AVAL é 2 (BPR)')
    emitir(tipo.eq('2') & oat.eq('1') & elg.eq('1') & conc.isin(['1', '3']), 'FLG_OAT',
           'Obra avaliada por BPR não pode ser atípica')

    infra0, infrapar, orca0, ipca = referencias_incr(str(pasta))
    pares = pd.MultiIndex.from_arrays([tuc, a1])
    infraestrutura = tuc.isin(infra0) | pd.Series(pares.isin(infrapar), index=x.index)
    emitir(infraestrutura & tipo.ne('1') & elg.eq('1') & conc.isin(['1', '3']), 'Cd_TP_AVAL',
           'Registro de infraestrutura exige Cd_TP_AVAL igual a 1')
    emitir(tuc.isin(orca0) & tipo.ne('4') & elg.eq('1') & conc.isin(['1', '3']), 'Cd_TP_AVAL',
           'Registro de orçamento exige Cd_TP_AVAL igual a 4')

    vnr, iai = num('VL_VNR_UC'), num('VL_IAI_UC')
    emitir(vnr.gt(0) & iai.div(vnr).add(0.000001).gt(0.2), 'VL_IAI_UC',
           'Não aproveitamento do ativo superior a 20% do VNR')

    dt_imob = pd.to_datetime(col('Dt_Imob'), errors='coerce', dayfirst=True)
    dt_ref = pd.to_datetime(col('Dt_REF_DADOS'), errors='coerce', dayfirst=True)
    if dt_fim is not None:
        limite_data = pd.to_datetime(dt_fim, dayfirst=True)
        emitir(dt_ref.notna() & dt_ref.gt(limite_data), 'Dt_REF_DADOS',
               'Data de referência posterior à data final do trabalho')
    qtd, voc = num('Qtd_AIS'), num('VL_VOC')
    especial = tuc.isin(TUC_IPCA)

    emitir(especial & dt_ref.notna() & dt_imob.notna() & dt_ref.lt(dt_imob),
           'Dt_REF_DADOS', 'Data de referência anterior à data de imobilização')

    emitir(especial & qtd.notna() & qtd.le(0), 'Qtd_AIS',
           'Quantidade deve ser positiva para cálculo de atualização monetária')

    campos_voc = (
                    'VL_VOC_VF',
                    'VL_VOC_COM',
                    'VL_VOC_CA',
                    'VL_VOC_JOA',
                )

    campos_aval = (
                        'VL_VOC_VF_AVAL',
                        'VL_VOC_COM_AVAL',
                        'VL_VOC_CA_AVAL',
                        'VL_VOC_JOA_AVAL',
                    )

    voc = num('VL_VOC')
    componentes_voc = pd.DataFrame(
                                        {campo: num(campo) for campo in campos_voc},
                                        index=x.index
                                    )

    componentes_aval = pd.DataFrame(
                                        {campo: num(campo) for campo in campos_aval},
                                        index=x.index
                                    )
    emitir(
                voc.lt(0),
                'VL_VOC',
                'VL_VOC não pode ser negativo'
            )


    for campo in campos_voc:
        emitir(
                    componentes_voc[campo].lt(0),
                    campo,
                    f'{campo} não pode ser negativo'
                )
    for campo in campos_aval:
        emitir(
                    componentes_aval[campo].lt(0),
                    campo,
                    f'{campo} não pode ser negativo'
                )
    validos_voc = (
                        voc.notna()
                        & componentes_voc.notna().all(axis=1)
                        & componentes_voc.ge(0).all(axis=1)
                        & voc.ge(0)
                    )    
    soma_voc = componentes_voc.sum(axis=1, min_count=4)
    tolerancia = 0.01
    emitir(
                validos_voc
                & (voc - soma_voc).abs().gt(tolerancia),
                'VL_VOC',
                'VL_VOC difere da soma de VL_VOC_VF, '
                'VL_VOC_COM, VL_VOC_CA e VL_VOC_JOA'
            )
    validos_aval = (
                        voc.notna()
                        & voc.ge(0)
                        & componentes_aval.notna().all(axis=1)
                        & componentes_aval.ge(0).all(axis=1)
                    )
    soma_aval = componentes_aval.sum(axis=1, min_count=4)

    emitir(
                validos_aval
                & soma_aval.gt(voc + tolerancia),
                'VL_VOC',
                'Soma dos componentes avaliados '
                '(VL_VOC_*_AVAL) superior a VL_VOC'
            )
    
    elegiveis = especial & dt_imob.notna() & dt_ref.notna() & dt_ref.ge(dt_imob) & qtd.gt(0) & voc.notna()
    ids = np.flatnonzero(elegiveis.to_numpy(dtype=bool))
    if len(ids):
        base = pd.DataFrame({'idx': ids, 'ini': dt_imob.iloc[ids].to_numpy(),
                             'ref': dt_ref.iloc[ids].to_numpy()})
        tabela = ipca[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'data', 'Nr_IPCA': 'indice'})
        ini = pd.merge_asof(base[['idx', 'ini']].sort_values('ini'),
                            tabela.rename(columns={'data': 'ini'}), on='ini', direction='backward')
        ref = pd.merge_asof(base[['idx', 'ref']].sort_values('ref'),
                            tabela.rename(columns={'data': 'ref'}), on='ref', direction='backward')
        fatores = (ini[['idx', 'indice']].rename(columns={'indice': 'ipca_ini'})
                   .merge(ref[['idx', 'indice']].rename(columns={'indice': 'ipca_ref'}), on='idx'))
        indices_invalidos = fatores['ipca_ini'].isna() | fatores['ipca_ref'].isna() | fatores['ipca_ini'].le(0)
        mascara = pd.Series(False, index=x.index)
        mascara.iloc[fatores.loc[indices_invalidos, 'idx'].to_numpy(dtype=int)] = True
        emitir(mascara, 'Dt_REF_DADOS', 'Índice IPCA ausente ou inválido para o período')
        ok = fatores.loc[~indices_invalidos].copy()
        if not ok.empty:
            idx = ok['idx'].to_numpy(dtype=int)
            atualizado = (voc.iloc[idx].to_numpy() / qtd.iloc[idx].to_numpy()
                          * ok['ipca_ref'].to_numpy() / ok['ipca_ini'].to_numpy())
            limite = np.where(tuc.iloc[idx].eq('535').to_numpy(),
                              ok['ipca_ref'].to_numpy() * 5000 / 3403.73, 1200.0)
            mascara = pd.Series(False, index=x.index)
            mascara.iloc[idx[atualizado < limite]] = True
            emitir(mascara, 'VL_VOC', 'Valor atualizado pelo IPCA inferior ao limite aplicável')

    return erros, ipca
```

</details>

---

<a id="funcao-10"></a>

## validar_duplicidades_global

Valida duplicidades em um conjunto de dados com base em um campo específico.

Verifica se há registros duplicados no campo especificado e retorna uma lista de erros contendo as informações das duplicidades encontradas.

### Assinatura

```python
# Consulte o código-fonte de validar_duplicidades_global
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dados` | `Não especificado` | Conjunto de dados a serem verificados. |
| `vistos` | `Não especificado` | Dicionário que armazena os códigos já vistos e suas respectivas linhas. |
| `deslocamento` | `Não especificado` | Valor de deslocamento para ajustar a linha atual em relação ao contexto do chamador. |
| `campo` | `Não especificado` | Nome do campo no registro que será usado para verificar duplicidades. |

### Retorno

**Tipo:** `Não especificado`

Lista de erros contendo informações sobre as duplicidades encontradas, ou uma lista vazia se não houver duplicidades.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_duplicidades_global(
                                    dados,
                                    vistos,
                                    deslocamento=0,
                                    campo="Cd_SubODI"
                                ):
    erros = []

    for indice, registro in enumerate(dados):
        codigo = registro.get(campo)
        if codigo is None or codigo == "":
            continue

        linha_atual = deslocamento + indice + 2

        if codigo in vistos:
            primeira_linha = vistos[codigo]
            erros.append({
                            "type": "value_error",
                            "loc": ("tabela", indice, campo),
                            "input": codigo,
                            "msg": (
                                f"Duplicidade no campo {campo}. "
                                f"Primeira ocorrência na linha "
                                f"{primeira_linha}."
                            ),
                            "etapa": deslocamento
                        })
        else:
            vistos[codigo] = linha_atual

    return erros
```

</details>

---

<a id="funcao-11"></a>

## conv_flut

Converte um valor em uma representação de ponto flutuante.

A função tenta converter o valor fornecido em um número de ponto flutuante. Se o valor for `None`, retorna `0.0`. Caso contrário, remove espaços em branco e substitui vírgulas por pontos antes da conversão.

### Assinatura

```python
def conv_flut(v) -> float:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `v` | `Não especificado` | Valor a ser convertido. Pode ser qualquer tipo, mas será tratado como uma string para a conversão. |

### Retorno

**Tipo:** `float`

Representação de ponto flutuante do valor fornecido.

### Dependências

- `float`
- `replace`
- `str`
- `strip`

<details>
<summary>Visualizar código-fonte</summary>

```python
def conv_flut(v) -> float:
    if v is None:
        return 0.0
    s = str(v).strip().replace(",", ".")
    if s == "":
        return 0.0
    return float(s)
```

</details>

---

<a id="funcao-12"></a>

## digitos

Extrai os dígitos de um valor fornecido.

Retorna uma string contendo apenas os caracteres numéricos do valor fornecido. Se o valor for nulo ou vazio, retorna uma string vazia.

### Assinatura

```python
def digitos(v) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `v` | `Não especificado` | Valor do qual os dígitos serão extraídos. |

### Retorno

**Tipo:** `str`

String contendo apenas os dígitos do valor fornecido.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def digitos(v) -> str:
    return "".join(ch for ch in str(v or "") if ch.isdigit())
```

</details>

---

<a id="funcao-13"></a>

## anl_lcmt

Analisa um dicionário de valores e retorna uma lista de erros encontrados.

A função percorre os itens do dicionário 'valores' e verifica se cada chave e valor atende a certas condições. Se não, adiciona mensagens de erro à lista 'erros'. As condições incluem verificação dos tipos de dados, formatação dos valores numéricos e sequência dos nomes das chaves.

### Assinatura

```python
def anl_lcmt(valores):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valores` | `dict` | Dicionário contendo os valores a serem analisados. |

### Retorno

**Tipo:** `list[str]`

Lista de mensagens de erro encontradas durante a análise.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def anl_lcmt(valores):
    n=0
    erros = []
    for chave, value in valores.items():
        if chave not in ['Id_OE_MOV','Id_OE_AMT','Cd_CC', 'Id_OE','Cd_CC','TP_OE','VL_SLD_INI','VL_SLD_REAV','Dt_REF']:
            if (chave[0:7] == "VL_Mes_"): n+=1
            if isinstance(value, str):
                if ('.' in value) and (',' in value):
                    erros.append(f"O campo '{chave}' não deve conter pontos como separadores de milhar.\n")
                try:
                    value_normalizado = float(value.replace(",", ".").strip())
                except ValueError:
                    erros.append(f"O campo '{chave}', tem um dado no formato inválido: {value}. Deve ser um número válido.\n")
            else:
                raise erros.append(f"O campo '{chave}' não é do tipo esperado.\n")
            if isinstance(chave,str):
                if (chave[0:7] != "VL_Mes_") and (chave != 'VL_Total'):
                    erros.append(f"O nome do atributo, {chave}, não segue o padrão solicitado (VL_Mes_xx ou VL_Total).\n")
                if (chave[0:7] == "VL_Mes_"):
                    if int(chave[7:])!=n:
                        erros.append(f"O campo '{chave}' não segue o padrão sequencial esperado: 'VL_Mes_{n}' era esperado.\n")
            else:
                erros.append(f"Atributo não é do tipo esperado.\n")
    return erros
```

</details>

---

<a id="funcao-14"></a>

## calc_digito

Calcula um dígito verificador para o CNPJ.

Esta função calcula um dígito verificador para o CNPJ com base em uma posição específica (1 ou 2). Utiliza pesos específicos e realiza cálculos de soma ponderada seguidos por uma operação de módulo para determinar o dígito.

### Assinatura

```python
def calc_digito(cnpj, posicao):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cnpj` | `Não especificado` | CNPJ completo como uma string. |
| `posicao` | `Não especificado` | Posição do dígito verificador a ser calculada (1 ou 2). |

### Retorno

**Tipo:** `Não especificado`

Dígito verificador calculado.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def calc_digito(cnpj, posicao):
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    if posicao==1:
        pesos = pesos[1:]
    total = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
    resto = total % 11
    return 0 if resto < 2 else 11 - resto
```

</details>

---

<a id="funcao-15"></a>

## validar_CNPJ

Valida um número de CNPJ.

Verifica se o valor fornecido é um número de CNPJ válido, considerando os dígitos verificadores e a estrutura do número.

### Assinatura

```python
def validar_CNPJ(valor: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `str` | Número de CNPJ como uma string. |

### Retorno

**Tipo:** `str`

O número de CNPJ válido, caso seja válido. Caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é do tipo esperado (não é uma string).
- **`ValueError`**: Quando o número de caracteres é diferente de 14 ou todos os números são iguais.
- **`ValueError`**: Quando o valor não é um número decimal válido.
- **`ValueError`**: Quando o dígito de verificação não confere.

### Dependências

- `{'nome': 'math', 'categoria': 'import'}`
- `{'nome': 'calc_digito', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CNPJ(valor: str):
    if isinstance(valor, str):
        if (valor is None) or (isinstance(valor, float) and math.isnan(valor)) or (valor == '') or (str(valor) == '0'):
            return valor
        if len(valor) != 14 or valor == valor[0] * len(valor):
            raise ValueError(f' CNPJ inválido, número de caracteres diferente de 14 ou todos os números iguais.\n')
        try:
            valor_normalizado = int(valor.replace(",", ".").strip())
        except ValueError:
            raise ValueError(f" o valor deve ser um número decimal válido.\n")
        
        PRIDG = calc_digito(valor,1)
        SEGDG = calc_digito(valor,2)
        
        if valor[-2:-1] != str(PRIDG) or valor[-1:] != str(SEGDG):
            raise ValueError(' CNPJ inválido, dígito de verificação não confere.')
        
        return valor
    else:
        raise ValueError(f" o valor não é do tipo esperado.\n")
```

</details>

---

<a id="funcao-16"></a>

## val_dt

Compara duas datas e retorna a primeira se elas forem iguais.

A função compara duas datas fornecidas como parâmetros. Se as datas forem idênticas, ela retorna a primeira data. Caso contrário, lança uma exceção indicando que há um erro na data de referência informada no arquivo correspondente à primeira data.

### Assinatura

```python
def val_dt(d1, d2):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `d1` | `Não especificado` | A primeira data a ser comparada. |
| `d2` | `Não especificado` | A segunda data a ser comparada. |

### Retorno

**Tipo:** `Não especificado`

A primeira data se as duas forem iguais; caso contrário, não há retorno explícito.

### Exceções

- **`ValueError`**: Quando as datas são diferentes, indicando um erro na data de referência informada no arquivo correspondente à primeira data.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def val_dt(d1, d2):
    if d1==d2:
        return d1
    else:
        raise ValueError(f"Verifique a data de referência informada no arquivo {d1}.")
```

</details>

---

<a id="funcao-17"></a>

## validar_decimal

Valida se um valor é um decimal válido, considerando opções para valores vazios e limites numéricos.

A função verifica se o valor fornecido é um número decimal válido. Permite que o valor esteja vazio ou seja limitado por valores mínimos e máximos. Caso contrário, lança exceções específicas.

### Assinatura

```python
def validar_decimal(valor, vazio=False, min_val=None, max_val=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser validado. |
| `vazio` | `Não especificado` | Indica se o valor pode estar vazio. Se True, retorna o valor vazio; caso contrário, lança uma exceção. |
| `min_val` | `Não especificado` | Valor mínimo permitido. Se fornecido e o valor for menor que este, lança uma exceção. |
| `max_val` | `Não especificado` | Valor máximo permitido. Se fornecido e o valor for maior que este, lança uma exceção. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, convertido para string.

### Exceções

- **`ValueError`**: Quando o valor não pode estar vazio e está vazio.
- **`ValueError`**: Quando o valor contém tanto ponto quanto vírgula como separador de milhar.
- **`ValueError`**: Quando o valor não é um número decimal válido.
- **`ValueError`**: Quando o valor é menor que o valor mínimo permitido.
- **`ValueError`**: Quando o valor é maior que o valor máximo permitido.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_decimal(valor, vazio=False, min_val=None, max_val=None):
    if pd.isna(valor):
        if vazio:
            return valor
        raise ValueError("não pode estar vazio.\n")

    valor = str(valor).strip()

    if "." in valor and "," in valor:
        raise ValueError("não use ponto como separador de milhar.\n")

    try:
        num = float(valor.replace(",", "."))
    except ValueError:
        raise ValueError("valor deve ser numérico decimal válido.\n")

    if min_val is not None and num < min_val:
        raise ValueError(f"valor deve ser >= {min_val}.\n")

    if max_val is not None and num > max_val:
        raise ValueError(f"valor deve ser <= {max_val}.\n")

    return valor
```

</details>

---

<a id="funcao-18"></a>

## validar_lista

Valida se um valor está presente em uma lista de valores permitidos.

Verifica se o valor fornecido é válido, considerando se pode estar vazio e se deve ser um número inteiro. Lança exceções caso contrário.

### Assinatura

```python
# Consulte o código-fonte de validar_lista
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser validado. |
| `valores_permitidos` | `Não especificado` | Lista de valores permitidos. |
| `descricao` | `Não especificado` | Descrição do valor para mensagens de erro. |
| `vazio` | `Não especificado` | Indica se o valor pode estar vazio. |

### Retorno

**Tipo:** `Não especificado`

Valor validado, ou None se permitido e for vazio.

### Exceções

- **`ValueError`**: Quando o valor é inválido, vazio (exceto quando permitido) ou não é um número inteiro (quando necessário).

### Dependências

- `math`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_lista(valor,
                  valores_permitidos,
                  descricao="valor",
                  vazio=False):

    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio:
            return valor
        raise ValueError(f"{descricao} não pode estar vazio.\n")

    v = str(valor).strip()
    exemplo = next(iter(valores_permitidos))

    if v == "" or v.lower() == "nan":
        if vazio:
            return valor
        raise ValueError(f"{descricao} não pode estar vazio.\n")
    
    if isinstance(exemplo, int):
        try:
            valor_int = int(v)
        except ValueError:
            raise ValueError(f"{descricao} deve ser um número inteiro.\n")

    if v not in valores_permitidos:
        raise ValueError(f"{descricao} '{v}' não é um código válido.\n")

    return valor
```

</details>

---

<a id="funcao-19"></a>

## validar_data

Valida uma data no formato aaaa/mm/dd.

Verifica se o valor fornecido é uma data válida no formato aaaa/mm/dd. Se o valor for vazio e permitido, retorna o valor original; caso contrário, lança um erro.

### Assinatura

```python
def validar_data(valor: Optional[str], vazio=False):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Optional[str]` | Valor a ser validado como data. |
| `vazio` | `bool` | Indica se o valor vazio é permitido. |

### Retorno

**Tipo:** `str`

Valor da data validado e formatado.

### Exceções

- **`ValueError`**: Quando a data está vazia e não é permitido, ou quando o formato da data é inválido.

### Dependências

- `datetime.date`
- `datetime.datetime`
- `math`
- `re`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_data(valor: Optional[str], vazio=False):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return valor
        raise ValueError(" data não pode estar vazia.\n")

    v = str(valor).strip().lower()
    if v == "" or v == "nan":
        if vazio: return valor
        raise ValueError(" data não pode estar vazia.\n")
    valor = str(valor).strip()
    if not re.match(r'^\d{4}/\d{2}/\d{2}$', valor):
        raise ValueError(" data deve estar no formato aaaa/mm/dd.\n")
    try:
        data = datetime.strptime(valor, "%Y/%m/%d").date()
    except ValueError:
        raise ValueError(" data inválida.\n")
    return valor
```

</details>

---

<a id="funcao-20"></a>

## validar_texto

Valida um texto com base em várias regras de validação.

A função valida um valor de texto, verificando se ele está vazio, contém caracteres inválidos, possui comprimento máximo e se pertence a um domínio específico. Lança exceções caso as regras não sejam atendidas.

### Assinatura

```python
# Consulte o código-fonte de validar_texto
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `str` | O valor de texto a ser validado. |
| `campo` | `str` | Nome do campo sendo validado, usado para mensagens de erro. |
| `vazio` | `bool` | Se True, permite que o valor esteja vazio e retorna uma string vazia em vez de um erro. |
| `max_len` | `int` | Comprimento máximo permitido para o valor. Se None, não há restrição de comprimento. |
| `dominio` | `list[str]` | Lista de valores válidos que o campo pode assumir. Se None, não há restrição de domínio. |
| `caracteres_invalidos` | `set[str]` | Conjunto de caracteres inválidos permitidos no valor. Se None, usa o conjunto padrão {"\|"}. |

### Retorno

**Tipo:** `str`

O valor validado, caso não haja erros.

### Exceções

- **`ValueError`**: Quando o valor está vazio e vazio=False ou quando o valor excede o comprimento máximo permitido.

### Dependências

- `math`
- `unicodedata`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_texto(valor: str, campo: str, vazio=False, max_len=255, dominio = None,
    caracteres_invalidos=None,):
    if dominio is None:
        dominio = []
    if caracteres_invalidos is None:
        caracteres_invalidos = {"|"}
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return ""
        raise ValueError(f" campo '{campo}' não pode ser vazio.")
    valor = str(valor).strip()
    if valor == "" or valor.lower() == "nan":
        if vazio: return ""
        raise ValueError(f" {campo} não pode estar vazio.")
    
    encontrados = [
                        caractere
                        for caractere in caracteres_invalidos
                        if caractere in valor
                    ]

    if encontrados:
        representacao = ", ".join(
                                    repr(caractere)
                                    for caractere in encontrados
                                )

        raise ValueError(
                            f"O campo '{campo}' contém caractere(s) inválido(s) "
                            f"para o formato do arquivo: {representacao}."
                        )
    caracteres_invalidos = []
    caracteres_permitidos = {
                                "\t",
                                "\r",
                                "\n", 
                            }

    for posicao, caractere in enumerate(valor):
        codigo = ord(caractere)
        categoria = unicodedata.category(caractere)

        if categoria == "Cc" and caractere not in caracteres_permitidos:
            caracteres_invalidos.append({
                                            "posicao": posicao,
                                            "codigo": f"U+{codigo:04X}",
                                            "nome": unicodedata.name(
                                                caractere,
                                                "CARACTERE DE CONTROLE",
                                            ),
                                        })

    if caracteres_invalidos:
        detalhes = ", ".join(
                                f"posição {item['posicao']}: "
                                f"{item['codigo']} ({item['nome']})"
                                for item in caracteres_invalidos
                            )

        raise ValueError(
                            f"O campo '{campo}' contém caractere(s) de controle "
                            f"inválido(s): {detalhes}."
                        )
    if max_len and len(valor) > max_len:
        raise ValueError(f" {campo} excede {max_len} caracteres.\n")
    if (dominio != []) and (valor not in dominio):
        raise ValueError(f' seguir o padrão fornecido no manual de dados {dominio}.\n')
    return valor
```

</details>

---

<a id="funcao-21"></a>

## validar_inteiro

Valida se um valor é um número inteiro positivo dentro de um intervalo opcional.

Verifica se o valor fornecido é um número inteiro positivo e, opcionalmente, se está dentro de um intervalo definido por `min_val` e `max_val`. Também permite que o campo esteja vazio dependendo do parâmetro `vazio`.

### Assinatura

```python
def validar_inteiro(valor: str, campo: str, min_val=None, max_val=None, vazio=False):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `str` | Valor a ser validado, fornecido como uma string. |
| `campo` | `str` | Nome do campo sendo validado, usado para mensagens de erro. |
| `min_val` | `Não especificado` | Valor mínimo permitido. Se None, não há verificação mínima. |
| `max_val` | `Não especificado` | Valor máximo permitido. Se None, não há verificação máxima. |
| `vazio` | `Não especificado` | Se True e o valor estiver vazio, retorna uma string vazia em vez de lançar um erro. |

### Retorno

**Tipo:** `str`

Valor validado como uma string. Retorna a mesma string original se for válido.

### Exceções

- **`ValueError`**: Quando o valor é None, vazio ou não pode ser convertido em um número inteiro positivo. Também quando o valor está fora dos limites definidos por `min_val` e `max_val`.

### Dependências

- `math`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_inteiro(valor: str, campo: str, min_val=None, max_val=None, vazio=False):
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        if vazio: return ""
        raise ValueError(f" campo '{campo}' não pode ser vazio.")

    v = str(valor).strip().lower()
    if v == "" or v == "nan":
        if vazio: return ""
        raise ValueError(f" {campo} não pode estar vazio.")

    if not v.isdigit():
        raise ValueError(f" {campo} deve ser um número inteiro positivo.")
    num = int(v)
    
    if min_val is not None and num < min_val:
        raise ValueError(f" {campo} deve ser >= {min_val}.")
    if max_val is not None and num > max_val:
        raise ValueError(f" {campo} deve ser <= {max_val}.")
    return v
```

</details>

---

<a id="funcao-22"></a>

## validar_projeto_pep

Valida os parâmetros de um projeto PEP.

Verifica se o código do subódio (Cd_SubODI) está preenchido e não excede o limite de caracteres, levantando uma exceção caso contrário. A validação é condicional à flag FLG_PER.

### Assinatura

```python
def validar_projeto_pep(Cd_SubODI: Optional[str], FLG_PER: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Cd_SubODI` | `Optional[str]` | Código do subódio, que deve ser informado se a flag FLG_PER for '1'. |
| `FLG_PER` | `str` | Flag de permissão que determina se o Cd_SubODI deve ser validado. |
| `linha` | `str` | Número da linha onde a validação ocorreu, usada para informar erros específicos. |

### Exceções

- **`ValueError`**: Quando FLG_PER é '1' e Cd_SubODI não está preenchido ou excede o limite de caracteres.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_projeto_pep(Cd_SubODI: Optional[str], FLG_PER: str, linha: str):
    if FLG_PER == "1":
        if not Cd_SubODI:
            raise ValueError(f" Cd_SubODI deve ser informada, linha {linha}, se for apropriação direta usar APR_DIR.\n")
        if len(Cd_SubODI) > 255:
            raise ValueError(f" Cd_SubODI, linha {linha}, maior do que o número de caracteres permitido.\n")
```

</details>

---

<a id="funcao-23"></a>

## validar_tuc_ti

Valida a combinação de TUC (Tipo de Unidade de Consumo) e TI (Tipo de Instalação).

Verifica se a combinação de TUC, TI, linha e Nr_A1 é válida de acordo com regras específicas. Lança exceções para combinações inválidas.

### Assinatura

```python
def validar_tuc_ti(Nr_TUC: str, Nr_TI: str, linha: str, Nr_A1: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TUC` | `str` | Tipo de Unidade de Consumo. |
| `Nr_TI` | `str` | Tipo de Instalação. |
| `linha` | `str` | Linha associada à combinação TUC-TI. |
| `Nr_A1` | `str` | Valor de A1 associado à combinação TUC-TI. |

### Exceções

- **`ValueError`**: Quando a combinação de Nr_TUC e Nr_TI não é válida de acordo com as regras especificadas.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tuc_ti(Nr_TUC: str, Nr_TI: str, linha: str, Nr_A1: str):
    if Nr_TI in {"10","11","12","13","14","15","16","17","18","19"}:
        raise ValueError(f" TUC {Nr_TUC} na TI {Nr_TI}, que não é típica de distribuidora, linha {linha}.\n")
    if (Nr_TUC == "570") and (Nr_TI not in {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}):
        raise ValueError(f" TUC 570 (Transformador de força) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "190") and (Nr_A1 != '3') and (Nr_TI in {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}):
        raise ValueError(f" TUC 190 (condutor) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "295") and (Nr_TI not in {"93","96"}):
        raise ValueError(f" TUC 295 (Medidor) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "535") and (Nr_TI not in {"99"}):
        raise ValueError(f" TUC 535 (Software) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "615") and (Nr_TI in {"20","21","22","23","24","25","26","27","28","29",
                                    "30","31","32","33","34","35","36","37","38","39",
                                    "50","51","52","53","54","55","56","57","58","59",
                                    "60","61","62","63","64","65","66","67","68","69",
                                    "10","11","12","13","14","15","16","17","18","19",
                                    "40","41","42","43","44","70","72","80","82","90",
                                    "92","93","94","96","97","98","99"}):

        raise ValueError(f" TUC 615 (Veículos) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "205") and (Nr_TI in {"20","21","22","23","30","31","32","33","34","50","51",
                                     "52","53","54","10","11","12","13","14","15","16","17",
                                     "18","19","40","41","42","43","44","70","71","72","80",
                                     "81","82","90","91","92","93","94","96","97","98","99"}):
        raise ValueError(f" TUC 205 (Direito, Marca, Patente) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "255") and (Nr_A1 in {'1'}) and (Nr_TI in {"20","21","22","23","24","25","26","27","28","29",
                                                        "30","31","32","33","34","35","36","37","38","39",
                                                        "50","51","52","53","54","55","56","57","58","59",
                                                        "60","61","62","63","64","65","66","67","68","69",
                                                        "10","11","12","13","14","15","16","17","18","19"}):
        raise ValueError(f" TUC 255 (poste) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "255") and (Nr_A1 in {'2'}) and (Nr_TI in {"40","41","42","43","93","96","20","21","22","23","24",
                                                        "30","31","32","33","34","50","51","52","53","54",
                                                        "60","61","62","63","64","10","11","12","13","14",
                                                        "15","16","17","18","19"}):
        raise ValueError(f" TUC 255 (torre) não pode estar na TI {Nr_TI}, linha {linha}.\n")
    if (Nr_TUC == "565") and (Nr_TI not in {"40","41","42","43"}):
        raise ValueError(f"TUC 565 (transformador de distribuição) não pode estar na TI {Nr_TI}, linha {linha}.\n")
```

</details>

---

<a id="funcao-24"></a>

## validar_tucs_proibidos

Valida se um TUC (Tipo de Unidade de Consumo) está na lista de proibidos.

Verifica se o TUC fornecido está na lista de TUCs proibidos e, em caso afirmativo, lança uma exceção com a descrição do TUC e a linha onde foi identificado.

### Assinatura

```python
def validar_tucs_proibidos(Nr_TUC: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TUC` | `str` | Código do TUC a ser validado. |
| `linha` | `str` | Linha onde o TUC foi identificado. |

### Exceções

- **`ValueError`**: Quando o TUC está na lista de proibidos, indicando que não deveria existir em distribuidora.

### Dependências

- `{'nome': 'ValoresTUC.descricao_por_codigo', 'tipo': 'função', 'categoria': 'chamada', 'descricao': 'Função utilizada para obter a descrição do TUC com base no código.'}`
- `{'nome': 'ValueError', 'tipo': 'exceção', 'categoria': 'chamada', 'descricao': 'Exceção lançada quando o TUC está na lista de proibidos.'}`
- `{'nome': 'int', 'tipo': 'função', 'categoria': 'chamada', 'descricao': 'Função utilizada para converter o código do TUC em um número inteiro.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tucs_proibidos(Nr_TUC: str, linha: str):
    TUC_PROIBIDOS = {
                        "100","105","110","112","115","140","145","150","155","170","175","185","225","240",
                        "245","260","275","280","300","320","335","350","360","365","370","390","405","420",
                        "425","430","435","440","470","475","490","500","505","510","515","525","530","585",
                        "590","595","600"
                    }
    if Nr_TUC in TUC_PROIBIDOS:
        nome = ValoresTUC.descricao_por_codigo(int(Nr_TUC))
        raise ValueError(f"TUC {Nr_TUC} ({nome}) não deveria existir em distribuidora, linha {linha}.\n")
```

</details>

---

<a id="funcao-25"></a>

## validar_cabos

Valida os valores dos cabos de acordo com regras específicas.

A função verifica se os valores dos cabos (Nr_TUC, Nr_A1, Nr_A3, Nr_A4, Nr_A5) estão dentro das regras estabelecidas. Se algum valor não atender à regra, uma exceção ValueError é lançada com uma mensagem descrevendo o problema.

### Assinatura

```python
def validar_cabos(Nr_TUC: str, Nr_A1: str, Nr_A3: str, Nr_A4: str, Nr_A5: str, v_UND: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TUC` | `str` | Número de Unidade de Transmissão (TUC). |
| `Nr_A1` | `str` | Número de Aparelho 1. |
| `Nr_A3` | `str` | Número de Aparelho 3. |
| `Nr_A4` | `str` | Número de Aparelho 4. |
| `Nr_A5` | `str` | Número de Aparelho 5. |
| `v_UND` | `str` | Unidade de medida (UND). |
| `linha` | `str` | Número da linha. |

### Exceções

- **`ValueError`**: Quando o valor de Nr_TUC não é '190' e Nr_A1 não é '3' ou '03'.
- **`ValueError`**: Quando UNI é 'M' ou 'MT' e Nr_A3 é '01', indicando que o cabo nu deve ser kg.
- **`ValueError`**: Quando UNI é 'KG' e Nr_A3 não é '01', indicando que o cabo nu deve ser m.
- **`ValueError`**: Quando Nr_A3 é '01' e Nr_A5 não é '01'.
- **`ValueError`**: Quando Nr_A4 está em um dos grupos específicos (grupo_a5_1, grupo_a5_2 ou grupo_a5_3) e Nr_A5 não é o valor esperado.
- **`ValueError`**: Quando Nr_A4 está em um dos grupos todos_multi e Nr_A5 é '01' enquanto Nr_A3 não é '01'.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cabos(Nr_TUC: str, Nr_A1: str, Nr_A3: str, Nr_A4: str, Nr_A5: str, v_UND: str, linha: str):
    if (Nr_TUC != "190") and (Nr_A1 not in {"3","03"}):
        return
    
    Nr_A3 = str(Nr_A3).zfill(2)
    Nr_A4 = str(Nr_A4).zfill(2)
    Nr_A5 = str(Nr_A5).zfill(2)
    UNI = str(v_UND).upper()

    if (UNI in ['M','MT']) and (Nr_A3 == '01'):
        raise ValueError(f" cabo nu deve ser kg, linha {linha}.\n")
    
    if (UNI in ['KG']) and (Nr_A3 != '01'):
        raise ValueError(f" cabo nu deve ser m, linha {linha}.\n")

    if Nr_A3 in {"01"} and Nr_A5 != "01":
        raise ValueError(f" cabo nu deve ter A5=1, linha {linha}.\n")

    if Nr_A3 not in {"01"}:
        grupo_a5_1 = {"60","62","64","65","66"}
        grupo_a5_2 = {"61","63","67","68","69","70"}
        grupo_a5_3 = {
                        "71","72","73","74","75","76","77","78","79","57","80","81","82",
                        "58","83","84","85","59","19","86","87","88","89","90","91","92",
                        "93","94","95"
                     }

        if( Nr_A4 in grupo_a5_1) and (Nr_A5 != "01"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=01, linha {linha}.\n")

        if (Nr_A4 in grupo_a5_2) and (Nr_A5 != "02"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=02, linha {linha}.\n")

        if (Nr_A4 in grupo_a5_3) and (Nr_A5 != "03"):
            raise ValueError(f" cabo multi-condutor A4={Nr_A4} deveria ter A5=03, linha {linha}.\n")

        todos_multi = grupo_a5_2 | grupo_a5_3
        if Nr_A4 in todos_multi and Nr_A5 == "01" and Nr_A3 not in {"01"}:
            raise ValueError(f" cabo multi-condutor com A5=1 inválido, linha {linha}.\n")

    return
```

</details>

---

<a id="funcao-26"></a>

## validar_administracao

Valida se a conta contábil (Cd_CC) é compatível com o número de TI (Nr_TI).

A função verifica se o número de TI está na lista de TIs administrativas e se a conta contábil não está na lista de contas administrativas permitidas. Se uma dessas condições for verdadeira, um erro é lançado.

### Assinatura

```python
def validar_administracao(Nr_TI: str, Cd_CC: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TI` | `str` | Número do TI a ser validado. |
| `Cd_CC` | `str` | Código da conta contábil a ser validada. |
| `linha` | `str` | Número da linha onde ocorreu o erro, para fins de referência. |

### Exceções

- **`ValueError`**: Quando o número de TI está na lista de TIs administrativas e a conta contábil não está na lista de contas administrativas permitidas. A mensagem de erro inclui o número do TI e o número da linha.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_administracao(Nr_TI: str, Cd_CC: str, linha: str):
    TIs_admin = {"70","71","72","90","91","94","99"}
    contas_admin = {"123340101","123340103","123340199","123240101","123240103","123240104","123240105","123240106"}
    if Nr_TI in TIs_admin and Cd_CC not in contas_admin:
        raise ValueError(f" para TI {Nr_TI} a conta contábil deve ser de administração, linha {linha}.\n")
```

</details>

---

<a id="funcao-27"></a>

## validar_torre_poste

Valida a torre ou poste com base em seus identificadores e linha.

A função verifica se os identificadores de TI, TUC e A1 estão dentro dos critérios especificados para validar a torre ou poste. Se não atender aos critérios, lança um erro ValueError com uma mensagem indicando o problema na linha fornecida.

### Assinatura

```python
def validar_torre_poste(Nr_TI: str, Nr_TUC: str, Nr_A1: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TI` | `str` | Identificador da TI (Tipo de Instalação). |
| `Nr_TUC` | `str` | Identificador da TUC (Tipo de Unidade de Comunicação). |
| `Nr_A1` | `str` | Identificador do A1 (Tipo de Estrutura). |
| `linha` | `str` | Número da linha onde ocorreu a validação. |

### Exceções

- **`ValueError`**: Quando o identificador de TI não está em TIs_LT_LD e Nr_TUC é '255' e Nr_A1 é '2', indicando que a torre está em TI diferente de LT/LD.
- **`ValueError`**: Quando o identificador de TI está em TIs_LT_LD e Nr_TUC é '255' e Nr_A1 é '1', indicando que o poste está em TI de LT/LD.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_torre_poste(Nr_TI: str, Nr_TUC: str, Nr_A1: str, linha: str):
    TIs_LT_LD = {"24","25","26","27","28","29","35","36","37","38","39","55","56","57",
                 "58","59","60","61","62","63","64"}
    if Nr_TI not in TIs_LT_LD and Nr_TUC == "255" and Nr_A1 == "2":
        raise ValueError(f" torre em TI diferente de LT/LD, linha {linha}.\n")
    if Nr_TI in TIs_LT_LD and Nr_TUC == "255" and Nr_A1 == "1":
        raise ValueError(f" poste em TI de LT/LD, linha {linha}.\n")
```

</details>

---

<a id="funcao-28"></a>

## validar_FLG_PER

Valida a flag de período (FLG_PER) com base na data de inserção (v_dt_IMB) e na data de referência.

A função verifica se a flag FLG_PER está corretamente definida em relação à data de inserção e à data de referência. Se a data de inserção for anterior à data de referência, FLG_PER deve ser '1'. Caso contrário, FLG_PER deve ser '0'. Em caso de inconformidade, uma exceção ValueError é lançada com uma mensagem indicando a linha em que ocorreu o erro.

### Assinatura

```python
def validar_FLG_PER(v_dt_IMB: str, v_PER: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `v_dt_IMB` | `str` | Data de inserção no formato 'YYYY/MM/DD'. |
| `v_PER` | `str` | Flag de período ('0' ou '1'). |
| `linha` | `str` | Número da linha em que a validação ocorre. |

### Exceções

- **`ValueError`**: Quando FLG_PER não está de acordo com as regras estabelecidas para a data de inserção e a data de referência.

### Dependências

- `datetime.date`
- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG_PER(v_dt_IMB: str, v_PER: str, linha: str):
    Dt_REF = st.session_state.dt_ini
    Dt_IMB = datetime.strptime(v_dt_IMB, "%Y/%m/%d").date()
    if (Dt_IMB < Dt_REF) and (v_PER=="1"):
        raise ValueError(f" FLG_PER deveria ser '0', linha {linha}.\n")
    if (Dt_IMB >= Dt_REF) and (v_PER=="0"):
        raise ValueError(f" FLG_PER deveria ser '1', linha {linha}.\n")
```

</details>

---

<a id="funcao-29"></a>

## validar_cm

Valida o número de controle (Nr_CM) com base no número de identificação do órgão (Nr_TI).

A função verifica se o Nr_CM é válido conforme as regras específicas para órgãos estaduais (SE) e não estaduais. Para SE, o Nr_CM deve ter três algarismos numéricos, com o primeiro dígito entre 0 e 4 e o terceiro dígito entre 0 e 5. Para órgãos não estaduais, o Nr_CM deve ser vazio ou '999'.

### Assinatura

```python
def validar_cm(Nr_TI: str, Nr_CM: Optional[str], linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TI` | `str` | Número de identificação do órgão. |
| `Nr_CM` | `Optional[str]` | Número de controle associado ao órgão. Pode ser None, vazio ou '999' para órgãos não estaduais. |
| `linha` | `str` | Número da linha onde ocorreu a validação. |

### Exceções

- **`ValueError`**: Quando o Nr_CM não é válido de acordo com as regras especificadas para órgãos estaduais ou não estaduais.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cm(Nr_TI: str, Nr_CM: Optional[str], linha: str):
    TIs_SE = {"20","21","22","23","30","31","32","33","34","50","51","52","53","54"}
    Nr_CM = str(Nr_CM)
    if Nr_TI in TIs_SE:
        if not Nr_CM or len(Nr_CM) != 3:
            raise ValueError(f" Nr_CM, linha {linha}, deve ter 3 algarismos numéricos para SE.\n")
        if Nr_CM[0] not in {"0","1","2","3","4"}:
            raise ValueError(f" primeiro dígito de Nr_CM inválido ({Nr_CM[0]}), linha {linha}.\n")
        if Nr_CM[0] != "0":
            raise ValueError(f" primeiro dígito de Nr_CM não é de SE de distribuição, linha {linha}.\n")
        if Nr_CM[2] not in {"0","1","2","3","4","5"}:
            raise ValueError(f" terceiro dígito de Nr_CM inválido ({Nr_CM[2]}), linha {linha}.\n")
    else:
        if Nr_CM not in {None,"","999"}:
            raise ValueError(f" Nr_CM, linha {linha}, tem de ser vazio ou 999 quando não for SE.\n")
```

</details>

---

<a id="funcao-30"></a>

## validar_ti_distribuicao

Valida o número de TI (Tipo de Instalação) e linha fornecidos.

Verifica se o número de TI está dentro dos intervalos específicos para instalações de geração, transmissão ou DIT. Lança um erro com uma mensagem descrevendo a instalação correspondente.

### Assinatura

```python
def validar_ti_distribuicao(Nr_TI: str, linha: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TI` | `str` | Número de TI que será validado. |
| `linha` | `str` | Linha associada ao número de TI. |

### Exceções

- **`ValueError`**: Quando o número de TI está dentro dos intervalos específicos para instalações de geração, transmissão ou DIT. A mensagem indica a instalação correspondente.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ti_distribuicao(Nr_TI: str, linha: str):
    if 9 < int(Nr_TI) < 20:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de geração.\n")
    if 19 < int(Nr_TI) < 30:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de transmissão ou DIT.\n")
    if 59 < int(Nr_TI) < 65:
        raise ValueError(f" Nr_TI {Nr_TI}, linha {linha}, indica instalação de linha de transmissão.\n")
```

</details>

---

<a id="funcao-31"></a>

## validar_bem_individual

Sem resumo disponível.

### Assinatura

```python
# Consulte o código-fonte de validar_bem_individual
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `Nr_TI` | `str` |  |
| `Nr_TUC` | `str` |  |
| `Nr_A1` | `str` |  |
| `Nr_A2` | `str` |  |
| `Nr_A3` | `str` |  |
| `Nr_A4` | `str` |  |
| `Nr_A5` | `str` |  |
| `Nr_A6` | `str` |  |
| `Qtd` | `str` |  |
| `linha` | `str` |  |
| `Cd_UAR` | `str` |  |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_bem_individual(Nr_TI: str, Nr_TUC: str, Nr_A1: str, Nr_A2: str, Nr_A3: str, Nr_A4: str, 
                            Nr_A5: str, Nr_A6: str, Qtd: str, linha: str, Cd_UAR: str):
    regras = [
                {'TI_DE': 10, 'TI_ATE': 19, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 100, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 105, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 110, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 112, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 115, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 120, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 125, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 130, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 1,  'A1_ATE': 2, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 3,  'A1_ATE': 3, 'A2_DE': 69,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 135, 'A1_DE': 3,  'A1_ATE': 3, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 140, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 145, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 150, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 155, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 165, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 170, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 175, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 185, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 195, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 200, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 205, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 210, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 215, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 220, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 225, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 240, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 245, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 250, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 260, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 265, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 270, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 275, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 280, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 285, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 300, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 305, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 315, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 320, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 330, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 335, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 340, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 69,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 340, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 345, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 350, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 355, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 360, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 365, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 370, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 375, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 380, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 385, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 390, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 400, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 405, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 410, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 415, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 420, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 425, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 430, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 435, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 440, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 445, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 450, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 455, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 460, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 465, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 470, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 475, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 480, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 485, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 490, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 495, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 500, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 505, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 510, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 515, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 520, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 525, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 530, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 535, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 540, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 545, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 550, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 555, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 560, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 570, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 575, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 69,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 575, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 580, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 585, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 590, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 595, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 600, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 610, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 10, 'TI_ATE': 99, 'TUC': 615, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 23, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 34,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 34,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 20, 'TI_ATE': 39, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 99,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 30, 'TI_ATE': 34, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 54, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 34,  'A2_ATE': 90,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 160, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 99,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 34,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 50, 'TI_ATE': 69, 'TUC': 310, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 99,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 72, 'TI_ATE': 72, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 82, 'TI_ATE': 82, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
                {'TI_DE': 92, 'TI_ATE': 92, 'TUC': 395, 'A1_DE': 0,  'A1_ATE': 99, 'A2_DE': 0,  'A2_ATE': 99,'A3_DE': 0,  'A3_ATE': 99,'A4_DE': 0,  'A4_ATE': 99,'A5_DE': 0,  'A5_ATE': 99,'A6_DE': 0,  'A6_ATE': 99},
             ]

    Nr_TUC = int(Nr_TUC)
    Nr_TI = int(Nr_TI)
    Nr_A1 = int(Nr_A1)
    Nr_A2 = int(Nr_A2)
    Nr_A3 = int(Nr_A3) 
    Nr_A4 = int(Nr_A4) 
    Nr_A5 = int(Nr_A5) 
    Nr_A6 = int(Nr_A6) 
    Qtd = float(Qtd.replace(".", "").replace(",", "."))

    candidatos = [
                    r for r in regras
                    if (
                        r["TI_DE"] <= Nr_TI <= r["TI_ATE"]
                        and r["TUC"] == Nr_TUC
                        and all(
                            r[f"A{i}_DE"] <= valor <= r[f"A{i}_ATE"]
                            for i, valor in enumerate(
                                [Nr_A1, Nr_A2, Nr_A3, Nr_A4, Nr_A5, Nr_A6],
                                start=1,
                            )
                        )
                    )
                ]
    
    if candidatos and Qtd != 1.0 and Cd_UAR != "UAR":
        raise ValueError(
                            f"Bem de controle individual: TUC {Nr_TUC}, "
                            f"quantidade informada {Qtd}, deveria ser 1. "
                            f"ID: {linha}, Cd_UAR = {Cd_UAR}."
                        )
```

</details>

---

<a id="funcao-32"></a>

## localizar_arquivo

Localiza o primeiro arquivo CSV com um determinado prefixo em um caminho base.

Procura por arquivos CSV que começam com um prefixo específico no diretório fornecido e retorna o nome do primeiro arquivo encontrado. Caso nenhum arquivo seja encontrado, retorna `None`.

### Assinatura

```python
def localizar_arquivo(base_path: str, prefixo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `base_path` | `str` | Caminho base onde os arquivos serão procurados. |
| `prefixo` | `str` | Prefixo que deve ser presente no nome dos arquivos CSV. |

### Retorno

**Tipo:** `str | None`

Nome do primeiro arquivo CSV encontrado ou `None` se nenhum arquivo for encontrado.

### Dependências

- `glob`
- `os`

<details>
<summary>Visualizar código-fonte</summary>

```python
def localizar_arquivo(base_path: str, prefixo: str) -> str | None:
    arquivos = glob.glob(os.path.join(base_path, f"{prefixo}*.csv"))
    if arquivos:
        return arquivos[0]
    return None
```

</details>

---

<a id="funcao-33"></a>

## _decimal_incr

Converte um valor para um objeto Decimal, ajustando a formatação de casas decimais.

A função recebe um valor que pode estar em formato de string ou número e o converte em um objeto Decimal. Ela remove espaços em branco no início e fim da string, substitui vírgulas por pontos para garantir uma representação decimal válida.

### Assinatura

```python
def _decimal_incr(valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser convertido em Decimal. Pode ser um número ou uma string que representa um número. |

### Retorno

**Tipo:** `decimal.Decimal`

Objeto Decimal representando o valor fornecido, ajustado para o formato decimal.

### Dependências

- `decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _decimal_incr(valor):
    return Decimal(str(valor).strip().replace(",", "."))
```

</details>

---

<a id="funcao-34"></a>

## _validar_dominio_bpr

Valida se um código pertence ao domínio BPR.

Verifica se o código fornecido está dentro do domínio BPR utilizando a função `test` da classe `ValoresBPR`. Lança uma exceção caso o código não seja válido.

### Assinatura

```python
def _validar_dominio_bpr(codigo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `codigo` | `Não especificado` | Código que será validado. |

### Exceções

- **`ValueError`**: Quando o código não pertence ao domínio BPR.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_dominio_bpr(codigo):
    if not ValoresBPR.teste(codigo):
        raise ValueError("Cd_SISBASE não pertence ao domínio BPR")
```

</details>

---

<a id="funcao-35"></a>

## ler_dados_csv

Lê dados de um arquivo CSV em lotes e retorna uma lista de dicionários.

A função lê dados de um arquivo CSV em lotes especificados pelo tamanho do lote (`tam_lote`) e o número do lote (`nr_lote`). Ela retorna uma lista de dicionários, onde cada dicionário representa uma linha do arquivo CSV. A função também trata casos em que o arquivo está vazio ou ocorrem erros durante a leitura.

### Assinatura

```python
def ler_dados_csv(nome_arquivo, tam_lote = 50000, nr_lote = 1):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome_arquivo` | `Não especificado` | Nome do arquivo CSV a ser lido. |
| `tam_lote` | `Não especificado` | Tamanho de cada lote de leitura. |
| `nr_lote` | `Não especificado` | Número do lote a ser lido. |

### Retorno

**Tipo:** `[dict]`

Lista de dicionários, onde cada dicionário representa uma linha do arquivo CSV.

### Exceções

- **`UserWarning`**: Quando ocorre um erro durante a leitura do arquivo e o mesmo é capturado como `pd.errors.EmptyDataError`, indicando que o arquivo está vazio.

### Dependências

- `pandas`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def ler_dados_csv(nome_arquivo, tam_lote = 50000, nr_lote = 1):
    tabela = []
    df_PRheader = pd.read_csv(nome_arquivo, sep="|", header = None,
                        encoding="latin-1", 
                        nrows = 2,
                        dtype = str )
    if len(df_PRheader)>1:
        try:
            df_PR = pd.read_csv(nome_arquivo, sep="|", header = None, 
                                encoding = "latin-1", 
                                skiprows = 1 + tam_lote * (nr_lote - 1), 
                                nrows = tam_lote,
                                dtype = str ,
                                keep_default_na=False)
        except Exception as e:
            if isinstance(e, pd.errors.EmptyDataError):
                st.warning(f"Problemas em {nome_arquivo}, não tem linhas (vazio), começando em {max((tam_lote + 1) * (nr_lote - 1), 1)}, mais {tam_lote} linhas.")
                df_PR = df_PRheader
                tam_reader = 0
                return tabela, tam_reader
            st.write(e)
            raise UserWarning(f"Problemas em {nome_arquivo}, começando em {max((tam_lote + 1) * (nr_lote - 1), 1)}, mais {tam_lote} linhas.")

        df_PR.columns = df_PRheader.iloc[0].tolist()
        tabela.append(df_PR.to_dict(orient='records'))
        tam_reader = len(df_PR)
    else:
        df_PR = df_PRheader
        tam_reader = 0
    return tabela, tam_reader
```

</details>

---

<a id="funcao-36"></a>

## validar_lote

Valida um lote de dados com base em seu tipo.

Esta função valida um lote de dados utilizando diferentes classes de tabelas dependendo do tipo fornecido. Se o tipo não for reconhecido, retorna uma mensagem indicando que a tabela não está modelada. Em caso de erros de validação, captura e retorna esses erros com informações adicionais.

### Assinatura

```python
def validar_lote(dados_lote, tipo, p=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dados_lote` | `Não especificado` | Dados do lote que serão validados. |
| `tipo` | `Não especificado` | Tipo de tabela que deve ser utilizada para validar os dados. |
| `p` | `Não especificado` | Etapa atual do processo, utilizado em erros de validação. |

### Retorno

**Tipo:** `Não especificado`

Lista de erros de validação ou uma mensagem indicando que a tabela não está modelada.

### Dependências

- `{'nome': 'ValidationError', 'categoria': 'importado'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_lote(dados_lote, tipo, p=None):
    erros = []
    try:
        if tipo in ['AIS', 'AISant', 'AISat']:
            TabelaAIS(**dados_lote)
        elif tipo in ['MOP']:
            TabelaMOP_FOPAG(**dados_lote)
        elif tipo in ['MOP_RUBRICAS']:
            TabelaMOP_RUBR(**dados_lote)
        elif tipo in ['MOP_SERVICOS']:
            TabelaMOP_SERV(**dados_lote)
        elif tipo in ['BS_ABT']:
            TabelaST_AB(**dados_lote)
        elif tipo in ['BS_FP']:
            TabelaST_FP(**dados_lote)
        elif tipo=='ROS':
            TabelaROS(**dados_lote)
        elif tipo=='DSC_CLS_CUSTO':
            TabelaDSCCLS(**dados_lote)
        elif tipo=='LST_FCUM':    
            TabelaLSTFCUM(**dados_lote)
        elif tipo=='LST_MAT':
            TabelaLSTMAT(**dados_lote)
        elif tipo=='LST_SERV':
            TabelaLSTSER(**dados_lote)
        elif tipo=='ROA':
            TabelaROA(**dados_lote)
        elif tipo=='ROD':
            TabelaROD(**dados_lote)
        elif tipo=='COMERCIAL_MEDIDORES':
            TabelaMed(**dados_lote)
        elif tipo=='NT_COM':
            TabelaNTcom(**dados_lote)
        elif tipo=='NT_CMU':
            TabelaNTcmu(**dados_lote)
        elif tipo=='OE_MOV':
            TabelaOEmov(**dados_lote)
        elif tipo=='OE_AMO':
            TabelaOEamt(**dados_lote)
        elif tipo == 'OE_SDINIC':
            TabelaOEsldini(**dados_lote)
        elif tipo == 'OE_REAV':
            TabelaOEreav(**dados_lote)
        elif tipo == 'OE_PLPTMOV':
            TabelaOEplptmov(**dados_lote)
        elif tipo == 'OE_PLPTAMO':
            TabelaOEplptamt(**dados_lote)
        elif tipo == 'OE_IRMOV':
            TabelaOEirmov(**dados_lote)
        elif tipo == 'OE_IRAMO':
            TabelaOEiramt(**dados_lote)
        elif tipo == 'OE_CCCMOV':
            TabelaOEcccmov(**dados_lote)
        elif tipo == 'OE_CCCAMO':
            TabelaOEcccamt(**dados_lote)
        elif tipo == 'OE_AJS':
            TabelaOEajt(**dados_lote)
        elif tipo == 'BP_EC':
            TabelaBPec(**dados_lote)
        elif tipo == 'BPFP_UAR':
            TabelaBPfpuar(**dados_lote)
        elif tipo == 'BP_UAR':
            TabelaBPuar(**dados_lote)
        elif tipo == 'REFORMADOS_INCREMENTAL':
            TabelaReform(**dados_lote)
        elif tipo == 'MUDANCA_PATRIMONIO':
            TabelaMp(**dados_lote)
        elif tipo == 'BAIXAS':
            TabelaBaixas(**dados_lote)
        elif tipo == 'DESC_ODI':
            TabelaDescODI(**dados_lote)
        elif tipo == 'PPBB':
            TabelaPPBB(**dados_lote)
        elif tipo == 'PCBB':
            TabelaPCBB(**dados_lote)
        elif tipo == 'INCR':
            TabelaINCR(**dados_lote)
        elif tipo == 'AO':
            TabelaAO(**dados_lote)
        elif tipo == 'ECDdepara':
            TabelaECD(**dados_lote)
        elif tipo == 'TDOMUC':
            TabelaTDOMUC(**dados_lote)
        elif tipo == 'LST_OBRAS_EMERG':
            TabelaLSTOBREMG(**dados_lote)
        elif tipo == 'LST_MAT_OBRAS_EMERG':
            TabelaLSTMATEMG(**dados_lote)
        elif tipo == 'ORIGEM_ATIVOS_INCREMENTAL':
            TabelaORATINCR(**dados_lote)
        elif tipo == 'LD_SALDO':
            TabelaLDSDS(**dados_lote)
        elif tipo == 'LD_LCMTO':
            TabelaLDLCTMO(**dados_lote)
        elif tipo == 'LD_PTD':
            TabelaLDPTD(**dados_lote)
        elif tipo == 'ROS_VAL':
            TabelaROSV(**dados_lote)
        elif tipo =='CD_SUBODI_AIS_ROS':
            TabelaCDSUBODIAIS(**dados_lote)
        elif tipo == 'COM_CA_BPC':
            TabelaCOMCABPC(**dados_lote)
        elif tipo == 'DT_ENERG':
            TabelaDTenerg(**dados_lote)
        elif tipo == 'OE_AGR':
            TabelaOEagr(**dados_lote)
        elif tipo == 'BS':
            Tabelabcserv(**dados_lote)
        elif tipo in ['ROAaicAT', 'ROAaicANT']:
            TabelaROA(**dados_lote)
        elif tipo in ['ROSaicAT', 'ROSaicANT']:
            TabelaROS(**dados_lote)
        elif tipo == 'ROS_ABT_AJST':
            TabelaRosAbtAjst(**dados_lote)
        elif tipo == 'ROS_ABT_CP':
            TabelaRosAbtCP(**dados_lote)
        elif tipo in ['ROAserv', 'RAserv']:
            TabelaRAs(**dados_lote)
        elif tipo in ['ROServ', 'RServ']:
            TabelaROServ(**dados_lote)
        else:
            return [f'Tabela {tipo} não modelada!']
    except ValidationError as e:
        for k in e.errors():
            k['etapa']=p
            erros.append(k)
    
    return erros
```

</details>

---

<a id="funcao-37"></a>

## validar_tabela_em_lotes_or

Valida uma tabela em lotes, utilizando um progresso visual e retornando erros encontrados.

A função divide os dados em lotes menores para validação, exibindo o progresso da operação. Cada lote é passado para a função `validar_lote` que retorna erros específicos. Os erros são acumulados e retornados no final.

### Assinatura

```python
def validar_tabela_em_lotes_or(dados, tamanho_lote=100, tipo='', deslocamento=0):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dados` | `Não especificado` | Dados a serem validados. |
| `tamanho_lote` | `Não especificado` | Tamanho de cada lote para validação. |
| `tipo` | `Não especificado` | Tipo dos dados, utilizado na exibição do progresso. |
| `deslocamento` | `Não especificado` | Deslocamento inicial para a indexação dos lotes. |

### Retorno

**Tipo:** `Não especificado`

Lista de erros encontrados durante a validação.

### Dependências

- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela_em_lotes_or(dados, tamanho_lote=100, tipo='', deslocamento=0):
    erros = []
    tabela = dados
    max_val = len(dados)
    a = st.progress(0,f"Rodando validação do {tipo}, 0/{max_val}.")
    for p in range(0, len(dados), tamanho_lote):
        a.progress(int((p / max_val) * 100), f"Rodando validação do {tipo}, {p}/{max_val}.")
        lote = {'tabela': tabela[p : (p + tamanho_lote)]}
        saida = validar_lote(lote, tipo, p)
        st.write(saida)
        erros.extend(validar_lote(lote, tipo, p))
    a.empty()
    return erros
```

</details>

---

<a id="funcao-38"></a>

## validar_tabela_em_lotes

Valida uma tabela em lotes, ajustando dinamicamente o tamanho do lote com base na duração da validação de cada lote.

A função valida uma tabela em lotes, ajustando dinamicamente o tamanho do lote com base na duração da validação de cada lote. O tamanho do lote é aumentado ou diminuído conforme necessário para otimizar a velocidade da validação. A função também exibe um progresso visual e captura erros durante a validação.

### Assinatura

```python
def validar_tabela_em_lotes(dados, tamanho_lote_inicial=300, tipo='', deslocamento=0):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `dados` | `Não especificado` | Dados que serão validados. |
| `tamanho_lote_inicial` | `Não especificado` | Tamanho inicial do lote de validação. |
| `tipo` | `Não especificado` | Tipo dos dados sendo validados (opcional). |
| `deslocamento` | `Não especificado` | Deslocamento aplicado aos índices durante a validação. |

### Retorno

**Tipo:** `Não especificado`

Lista de erros encontrados durante a validação.

### Exceções

- **`Exception`**: Qualquer exceção que ocorra durante a validação será capturada e re Lançada com uma mensagem de erro detalhada.

### Dependências

- `streamlit`
- `time`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela_em_lotes(dados, tamanho_lote_inicial=300, tipo='', deslocamento=0):
    erros = []
    tabela = dados
    max_val = len(dados)
    a = st.progress(0,f"Rodando validação do {tipo}, 0/{max_val}.")

    pos = 0
    tamanho_lote = tamanho_lote_inicial
    tamanho_min = 5
    tamanho_max = 2000
    alvo_segundos = 0.30
    fator_up = 1.25
    fator_down = 0.70
    pos = 0

    try:
        while pos < max_val:
            a.progress(int((pos / max_val) * 100), f"Rodando validação do {tipo}, {pos}/{max_val}. Passo otimizado: {tamanho_lote}.")
            lote_fim = min(pos + tamanho_lote, max_val)
            lote = {'tabela': tabela[pos:lote_fim]}
            inicio = time.time()
        
            erros.extend(validar_lote(lote, tipo, p = deslocamento + pos))
            
            duracao = time.time() - inicio
            
            if duracao < alvo_segundos * 0.7:
                tamanho_lote = int(min(tamanho_lote * fator_up, tamanho_max))
            elif duracao > alvo_segundos * 1.3:
                tamanho_lote = int(max(tamanho_lote * fator_down, tamanho_min))

            pos = lote_fim

            time.sleep(0.001)
    except Exception as e:
        st.write(f"Problema em {tipo}, {pos}. Mensagem {e}")
        st.write(lote)
        raise
    finally:
        a.empty()
    return erros
```

</details>

---

<a id="funcao-39"></a>

## anl_erro

Analisa e organiza erros em um DataFrame com base em uma lista de erros fornecida.

A função percorre uma lista de erros, verifica se cada erro é do tipo especificado e adiciona informações relevantes ao DataFrame `df_IMPR`. Se o erro não for do tipo esperado, ele é adicionado à lista de tipos de erro. A função retorna o DataFrame atualizado com as novas informações de erro e a lista de tipos de erro.

### Assinatura

```python
def anl_erro(erros, df_IMPR, tabela, tipo_erro = ['Erro de dependência, validação cruzada de campos.']):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `erros` | `Não especificado` | Lista de erros que serão analisados. |
| `df_IMPR` | `Não especificado` | DataFrame onde as informações dos erros serão adicionadas. |
| `tabela` | `Não especificado` | Nome da tabela associada aos erros. |
| `tipo_erro` | `Não especificado` | Lista inicial de tipos de erro a serem considerados. |

### Retorno

**Tipo:** `Não especificado`

Tupla contendo o DataFrame atualizado com as informações dos erros e a lista de tipos de erro.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def anl_erro(erros, df_IMPR, tabela, tipo_erro = ['Erro de dependência, validação cruzada de campos.']):
    if len(erros)>0:
        for erro in erros:
            try:
                if erro['msg'] not in tipo_erro:
                    if erro['msg'].find('Duplicidade') < 0:
                        tipo_erro += [erro['msg']]
                    elif 'Duplicidade de ocorrência.' not in tipo_erro:
                        tipo_erro += ['Duplicidade de ocorrência.']
                if erro['type'] == 'missing':
                    a = f"Falta o campo: {erro['loc'][2]}."
                    if len(df_IMPR[df_IMPR['Erro'] == a]) != 0:
                        a = ""
                elif erro['type'] == 'extra_forbidden':
                    a = f"Campo adicional: {erro['loc'][2]}."
                    if len(df_IMPR[df_IMPR['Erro'] == a]) != 0:
                        a = ""
                elif erro['msg'].find('Duplicidade') >= 0:
                    a = 'Duplicidade de ocorrência.'
                else:
                    try:
                        linha = erro['loc'][1] + 2 + erro['etapa']
                        a = f"No campo {erro['loc'][2]}, linha {linha}, o valor está como {'vazio' if erro['input']=='' else erro['input']}, isso provoca erro.\n"
                    except:
                        a = "Sem detalhe"
                if a != "":
                    if a != "Sem detalhe":
                        if a == 'Duplicidade de ocorrência.':
                            pr = {'Erro' : [erro['msg']],
                                  'Tipo' : [a],
                                  'Tabela' : [tabela]}
                        else:
                            pr = {'Erro' : [a],
                                  'Tipo' : [erro['msg']],
                                  'Tabela' : [tabela]}
                    else:
                        pr = {'Erro' : [erro['msg']],
                              'Tipo' : ['Erro de dependência, validação cruzada de campos.'],
                              'Tabela' : [tabela]}
                    if len(df_IMPR)==0:
                        df_IMPR = pd.DataFrame(pr)
                    else:
                        df_IMPR = pd.concat([df_IMPR, pd.DataFrame(pr)], ignore_index=True)
            except:
                if 'Estrutura não modelada no validador' not in tipo_erro:
                    tipo_erro += ['Estrutura não modelada no validador']
                pr = {'Erro' : [f'Tabela {tabela} não modelada para validação.'],
                      'Tipo' : ['Estrutura não modelada no validador'],
                      'Tabela' : [tabela]}
                if len(df_IMPR)==0:
                    df_IMPR = pd.DataFrame(pr)
                else:
                    df_IMPR = pd.concat([df_IMPR, pd.DataFrame(pr)], ignore_index=True)
                
    return df_IMPR, tipo_erro
```

</details>

---

<a id="funcao-40"></a>

## limpar_texto_latin1

Limpa um texto, substituindo caracteres não suportados pelo conjunto de caracteres Latin-1.

A função verifica se a entrada é uma string e, em caso afirmativo, encodifica-a no formato Latin-1, substituindo caracteres inválidos. Se a entrada não for uma string, ela é retornada inalterada.

### Assinatura

```python
def limpar_texto_latin1(s):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `s` | `Não especificado` | Texto que será limpo. |

### Retorno

**Tipo:** `Não especificado`

Texto limpo ou a entrada original, se não for uma string.

### Dependências

- `isinstance`

<details>
<summary>Visualizar código-fonte</summary>

```python
def limpar_texto_latin1(s):
    if isinstance(s, str):
        return s.encode("latin-1", errors="replace").decode("latin-1")
    return s
```

</details>

---

<a id="funcao-41"></a>

## gerar_relatorio_erros

Gera um relatório de erros com base em uma lista de erros fornecida.

A função agrupa os erros por campo, severidade e descrição, contabiliza a quantidade de ocorrências e fornece exemplos de identificadores. Utiliza expressões regulares para limpar as mensagens de erro e Streamlit para exibir um spinner durante a consolidação dos dados.

### Assinatura

```python
def gerar_relatorio_erros(lista_erros, nm_TBL="", tam_lote=1):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `lista_erros` | `Não especificado` | Lista de erros, onde cada erro pode ser um dicionário ou uma string. |
| `nm_TBL` | `Não especificado` | Nome da tabela associada aos erros. Padrão é uma string vazia. |
| `tam_lote` | `Não especificado` | Tamanho do lote de processamento. Padrão é 1. |

### Retorno

**Tipo:** `Não especificado`

DataFrame contendo o relatório de erros agrupados e formatado.

### Dependências

- `pandas`
- `re`
- `streamlit`

<details>
<summary>Visualizar código-fonte</summary>

```python
def gerar_relatorio_erros(lista_erros, nm_TBL="", tam_lote=1):
    agrupamento = {}

    regex_tags = re.compile(r"\[.*?\]")
    regex_linha = re.compile(
                                r"(?i)(linha|index|id)\s*[:_#-]?\s*\d+"
                            )
    regex_id = re.compile(
                            r"\[ID:\s*(.*?)\]",
                            flags=re.IGNORECASE
                        )

    with st.spinner(
                        f"Em progresso a consolidação dos erros do {nm_TBL}"
                    ):
        for erro in lista_erros:

            if isinstance(erro, dict):
                loc = erro.get("loc", ())
                msg_original = str(erro.get("msg", ""))
                etapa = erro.get("etapa", 0)
                tipo = erro.get("type", "")
                severidade = erro.get("severidade", "ERRO")
            else:
                loc = ()
                msg_original = str(erro)
                etapa = 0
                tipo = ""
                severidade = "ERRO"

            if not isinstance(loc, (tuple, list)):
                loc = ()

            indice_lote = next(
                                    (
                                        parte
                                        for parte in loc
                                        if isinstance(parte, int)
                                        and not isinstance(parte, bool)
                                    ),
                                    None
                                )


            if (
                    len(loc) >= 3
                    and isinstance(loc[-1], str)
                ):
                campo = loc[-1]

            elif tipo in ("missing", "extra_forbidden") and loc:
                campo = str(loc[-1])

            elif indice_lote is not None:
                campo = "Geral da Linha"

            else:
                campo = "Desconhecido"

            if indice_lote is not None:
                try:
                    index_linha = (
                        int(etapa or 0)
                        + indice_lote
                        + 2
                    )
                except (ValueError, TypeError):
                    index_linha = "?"
            else:
                index_linha = "?"

            if isinstance(erro, dict) and erro.get("nivel_agregacao"):
                id_exemplo = "Agregado"
            else:
                match_id = regex_id.search(msg_original)

                if match_id:
                    id_exemplo = match_id.group(1)
                else:
                    id_exemplo = str(index_linha)

            msg_limpa = regex_tags.sub("", msg_original)
            msg_limpa = regex_linha.sub("", msg_limpa)
            msg_limpa = re.sub(
                                    r"\s+",
                                    " ",
                                    msg_limpa
                                ).strip()

            if not msg_limpa:
                msg_limpa = "Erro não especificado"

            chave = (severidade, campo, msg_limpa)

            if chave not in agrupamento:
                agrupamento[chave] = {
                                        "Campo": campo,
                                        "Severidade": severidade,
                                        "Erro Padrão": msg_limpa,
                                        "Qtd": 0,
                                        "Exemplos": []
                                    }

            grupo = agrupamento[chave]
            grupo["Qtd"] += 1

            if (
                    len(grupo["Exemplos"]) < 10
                    and str(id_exemplo) not in grupo["Exemplos"]
                ):
                grupo["Exemplos"].append(str(id_exemplo))

    colunas = [
                    "Campo",
                    "Severidade",
                    "Descrição do Erro",
                    "Qtd",
                    "Exemplos (Amostra, linha do arquivo)",
                    "Nm_TAB"
                ]

    dados_finais = [
                        {
                            "Campo": grupo["Campo"],
                            "Severidade": grupo["Severidade"],
                            "Descrição do Erro": grupo["Erro Padrão"],
                            "Qtd": grupo["Qtd"],
                            "Exemplos (Amostra, linha do arquivo)": ", ".join(
                                grupo["Exemplos"]
                            ),
                            "Nm_TAB": nm_TBL
                        }
                        for grupo in agrupamento.values()
                    ]

    df = pd.DataFrame(dados_finais, columns=colunas)

    if not df.empty:
        df = df.sort_values(
                                by="Qtd",
                                ascending=False
                            ).reset_index(drop=True)

    return df
```

</details>

---

<a id="funcao-42"></a>

## col

Converte os valores de uma coluna em string e remove espaços em branco.

A função converte os valores da coluna especificada para o tipo string, substitui valores nulos por uma string vazia e remove qualquer espaço em branco no início ou fim dos valores.

### Assinatura

```python
def col(nome):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da coluna a ser processada. |

### Retorno

**Tipo:** `Não especificado`

Coluna processada com valores convertidos para string e espaços em branco removidos.

### Dependências

- `astype`
- `fillna`
- `str.strip`

<details>
<summary>Visualizar código-fonte</summary>

```python
def col(nome):
        return x[nome].astype("string").fillna("").str.strip()
```

</details>

---

<a id="funcao-43"></a>

## num

Converte uma coluna de texto em valores numéricos.

A função recebe um nome de coluna e retorna os valores convertidos para tipo numérico, substituindo vírgulas por pontos. Casos onde a conversão falha são tratados como NaN.

### Assinatura

```python
def num(nome):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da coluna que será convertida em valores numéricos. |

### Retorno

**Tipo:** `Não especificado`

Coluna com os valores convertidos para tipo numérico.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def num(nome):
        return pd.to_numeric(
                                col(nome).str.replace(",", ".", regex=False),
                                errors="coerce"
                            )
```

</details>

---

<a id="funcao-44"></a>

## col

Retorna uma série Pandas com os valores de uma coluna específica, convertidos para string e removendo espaços em branco.

A função verifica se o nome da coluna fornecido existe no DataFrame `x`. Se não existir, retorna uma série vazia. Caso contrário, retorna a coluna especificada como uma série de strings, com valores nulos substituídos por uma string vazia e espaços em branco removidos.

### Assinatura

```python
def col(nome):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da coluna a ser retornada. |

### Retorno

**Tipo:** `pd.Series`

Série Pandas contendo os valores da coluna especificada, convertidos para string e com espaços em branco removidos.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def col(nome):
        if nome not in x.columns:
            return pd.Series('', index=x.index, dtype='string')
        return x[nome].astype('string').fillna('').str.strip()
```

</details>

---

<a id="funcao-45"></a>

## num

Converte uma coluna de texto em valores numéricos.

A função recebe um nome de coluna e retorna os valores convertidos para tipo numérico, substituindo vírgulas por pontos. Casos onde a conversão falha são tratados como NaN.

### Assinatura

```python
def num(nome):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `nome` | `Não especificado` | Nome da coluna que será convertida em valores numéricos. |

### Retorno

**Tipo:** `Não especificado`

Coluna com os valores convertidos para tipo numérico.

### Dependências

- `pandas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def num(nome):
        return pd.to_numeric(col(nome).str.replace(',', '.', regex=False), errors='coerce')
```

</details>

---

<a id="funcao-46"></a>

## emitir

Emite erros de valor com base em uma máscara e um campo específico.

Itera sobre os índices onde a máscara é verdadeira e adiciona erros de valor para esses índices, associados ao campo fornecido e à mensagem de erro especificada.

### Assinatura

```python
def emitir(mascara, campo, mensagem):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `mascara` | `Não especificado` | Máscara que determina quais elementos devem gerar erros. |
| `campo` | `Não especificado` | Nome do campo associado ao erro. |
| `mensagem` | `Não especificado` | Mensagem de erro a ser exibida. |

### Dependências

- `numpy`

<details>
<summary>Visualizar código-fonte</summary>

```python
def emitir(mascara, campo, mensagem):
        if isinstance(mascara, pd.Series):
            indices = np.flatnonzero(mascara.fillna(False).to_numpy(dtype=bool))
        else:
            indices = np.flatnonzero(np.asarray(mascara, dtype=bool))
        for i in indices:
            erros.append({
                            'type': 'value_error',
                            'loc': ('tabela', int(i), campo),
                            'msg': f'Value error, {mensagem}',
                            'input': x.at[int(i), campo] if campo in x else None,
                            'ctx': {'error': ValueError(mensagem)},
                            'etapa': deslocamento,
                        })
```

</details>

---

<a id="funcao-47"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então cria a instância com esses valores armazenados internamente.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe criada.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamadas', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor 
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-48"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-49"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-50"></a>

## teste

Verifica se um código está presente no Enum.

A função verifica a existência de um código em uma coleção interna definida pelo método `_codigos` do objeto da classe.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Instância da classe que contém o método `_codigos`. |
| `codigo` | `str` | Código a ser verificado na coleção interna. |

### Retorno

**Tipo:** `bool`

True se o código estiver presente, False caso contrário.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        """Verifica se um código está presente no Enum."""
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-51"></a>

## descricao_por_codigo

Retorna a descrição associada a um código.

A função busca uma descrição em um mapa interno do objeto da classe para o código fornecido. Retorna `None` se o código não for encontrado no mapa.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa interno. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição associada ao código, ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de códigos para descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave fornecida e retorna o valor associado, ou `None` se a chave não existir.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        """Retorna a descrição associada a um código."""
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-52"></a>

## _mapa

Retorna um dicionário {código: descrição}, cacheado.

A função verifica se já existe um cache no objeto da classe. Se não existir, ele cria um cache com os códigos e descrições dos elementos da classe e o retorna. Caso contrário, simplesmente retorna o cache existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os elementos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos e os valores são descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        """Retorna um dicionário {codigo: descricao}, cacheado."""
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-53"></a>

## _codigos

Retorna todos os códigos válidos.

A função retorna um conjunto de strings que representam todos os códigos válidos disponíveis no contexto da classe chamada. A implementação utiliza o método `_mapa()` para obter a mapeamento dos códigos e, em seguida, extrai as chaves deste mapeamento.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_mapa()` para obter os códigos válidos. |

### Retorno

**Tipo:** `set[str]`

Conjunto de strings representando todos os códigos válidos.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método da classe que retorna o mapeamento dos códigos.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário para obter as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função para criar um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        """Retorna todos os códigos válidos."""
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-54"></a>

## teste

Verifica se um número está presente em uma coleção de objetos.

Itera sobre cada objeto na coleção e verifica se o primeiro elemento do valor associado a ele é igual ao número fornecido. Retorna `True` se encontrar, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, nro):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Coleção de objetos a serem verificados. |
| `nro` | `Não especificado` | Número que será procurado na coleção. |

### Retorno

**Tipo:** `bool`

Indica se o número foi encontrado (`True`) ou não (`False`).

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, nro):
        for valor in cls:
            if valor.value[0][0] == nro:
                return True
        return False
```

</details>

---

<a id="funcao-55"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então configura os atributos `_value_`, `_codigo` e `_descricao` da instância com esses valores.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamada', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-56"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-57"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-58"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-59"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-60"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-61"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-62"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então configura os atributos `_value_`, `_codigo` e `_descricao` da instância com esses valores.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamada', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-63"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-64"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-65"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-66"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-67"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-68"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-69"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então configura os atributos `_value_`, `_codigo` e `_descricao` da instância com esses valores.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamada', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-70"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-71"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-72"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-73"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-74"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-75"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-76"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então configura os atributos `_value_`, `_codigo` e `_descricao` da instância com esses valores.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamada', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-77"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-78"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-79"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-80"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-81"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-82"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-83"></a>

## __init__

Inicializa um objeto com um código e uma descrição.

Este método é responsável por configurar as propriedades `_codigo` e `_descricao` do objeto ao seu valor inicial fornecido.

### Assinatura

```python
def __init__(self, codigo: int, descricao: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância atual da classe. |
| `codigo` | `int` | Código associado ao objeto. |
| `descricao` | `str` | Descrição associada ao objeto. |

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def __init__(self, codigo: int, descricao: str):
        self._codigo = codigo
        self._descricao = descricao
```

</details>

---

<a id="funcao-84"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna o valor do atributo `_codigo` do objeto atual.

### Assinatura

```python
def codigo(self) -> int:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que chama o método. |

### Retorno

**Tipo:** `int`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> int:
        return self._codigo
```

</details>

---

<a id="funcao-85"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-86"></a>

## teste

Verifica se um número está presente em uma lista de códigos.

A função verifica se o número fornecido está contido na lista retornada pela chamada ao método `_codigos` da classe. Este método deve ser definido dentro da mesma classe e retornar uma lista de inteiros.

### Assinatura

```python
def teste(cls, nro: int) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |
| `nro` | `int` | Número inteiro a ser verificado na lista de códigos. |

### Retorno

**Tipo:** `bool`

True se o número está presente na lista, False caso contrário.

### Dependências

- `{'nome': '_codigos', 'categoria': 'método da classe', 'descricao': 'Método que deve retornar uma lista de inteiros.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, nro: int) -> bool:
        return nro in cls._codigos()
```

</details>

---

<a id="funcao-87"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao número fornecido.

Busca e retorna a descrição associada ao número passado como parâmetro, utilizando um método interno `_mapa()` que deve retornar um dicionário mapeando números para suas respectivas descrições.

### Assinatura

```python
def descricao_por_codigo(cls, nro: int) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, onde o método `_mapa()` é chamado. |
| `nro` | `int` | Número para o qual a descrição será buscada. |

### Retorno

**Tipo:** `str`

Descrição correspondente ao número fornecido, ou `None` se não encontrado.

### Dependências

- `{'nome': '_mapa', 'categoria': 'método interno', 'descricao': 'Método da classe que deve retornar um dicionário mapeando números para descrições.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, nro: int) -> str:
        return cls._mapa().get(nro)
```

</details>

---

<a id="funcao-88"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[int, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[int, str]`

Dicionário onde as chaves são códigos de método e os valores são descrições desses métodos.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[int, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-89"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é acessado através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[int]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[int]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[int]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-90"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele recebe um par de valores, onde o primeiro valor é usado como código e o segundo como descrição, e então configura os atributos `_value_`, `_codigo` e `_descricao` da instância com esses valores.

### Assinatura

```python
def __new__(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `valor` | `Não especificado` | Um par de valores, onde o primeiro é usado como código e o segundo como descrição. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `{'nome': 'object.__new__', 'categoria': 'chamada', 'descricao': 'Método usado para criar uma nova instância do objeto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, valor):
        codigo, descricao = valor
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-91"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-92"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-93"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-94"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-95"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-96"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-97"></a>

## teste

Verifica se um número está presente em uma coleção de objetos.

Itera sobre cada objeto na coleção e verifica se o primeiro elemento do valor associado a ele é igual ao número fornecido. Retorna `True` se encontrar, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, nro):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Coleção de objetos a serem verificados. |
| `nro` | `Não especificado` | Número que será procurado na coleção. |

### Retorno

**Tipo:** `bool`

Indica se o número foi encontrado (`True`) ou não (`False`).

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, nro):
        for valor in cls:
            if valor.value[0][0] == nro:
                return True
        return False
```

</details>

---

<a id="funcao-98"></a>

## testeQ5

Verifica se um valor específico está presente em uma coleção de objetos.

Itera sobre cada objeto na coleção e verifica se o primeiro elemento do segundo item da tupla retornada pelo atributo `value` é igual ao número fornecido. Retorna `True` se encontrar a correspondência, caso contrário, retorna `False`.

### Assinatura

```python
def testeQ5(cls, nro):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Coleção de objetos que serão iterados. |
| `nro` | `Não especificado` | Número a ser comparado com o primeiro elemento do segundo item da tupla retornada pelo atributo `value` dos objetos. |

### Retorno

**Tipo:** `bool`

Indica se o número foi encontrado na coleção de objetos.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def testeQ5(cls, nro):
        for valor in cls:
            if valor.value[0][5] == nro:
                return True
        return False
```

</details>

---

<a id="funcao-99"></a>

## __new__

Cria uma nova instância da classe.

Este método é responsável por criar e inicializar uma nova instância da classe. Ele aceita três parâmetros: `cls`, `codigo` e `descricao`. O valor de `cls` é a própria classe, enquanto `codigo` e `descricao` são usados para definir os atributos `_value_`, `_codigo` e `_descricao` da instância.

### Assinatura

```python
def __new__(cls, codigo, descricao):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | A própria classe. |
| `codigo` | `Não especificado` | O código associado à instância. |
| `descricao` | `Não especificado` | A descrição associada à instância. |

### Retorno

**Tipo:** `Não especificado`

A nova instância da classe.

### Dependências

- `object.__new__`

<details>
<summary>Visualizar código-fonte</summary>

```python
def __new__(cls, codigo, descricao):
        obj = object.__new__(cls)
        obj._value_ = codigo
        obj._codigo = codigo
        obj._descricao = descricao
        return obj
```

</details>

---

<a id="funcao-100"></a>

## codigo

Retorna o código associado ao objeto.

A função retorna uma string que representa o código armazenado no atributo `_codigo` do objeto atual (`self`).

### Assinatura

```python
def codigo(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `str`

Código associado ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def codigo(self) -> str:
        return self._codigo
```

</details>

---

<a id="funcao-101"></a>

## descricao

Retorna a descrição associada ao objeto.

A função retorna uma string que representa a descrição do objeto em questão. Não há parâmetros adicionais além de 'self', que é uma referência à instância da classe.

### Assinatura

```python
def descricao(self) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Referência à instância da classe. |

### Retorno

**Tipo:** `str`

A descrição associada ao objeto.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao(self) -> str:
        return self._descricao
```

</details>

---

<a id="funcao-102"></a>

## teste

Verifica se um código está presente na lista de códigos interna da classe.

A função verifica se o código fornecido existe dentro da lista de códigos retornada pelo método `_codigos` da própria classe. Retorna `True` se o código estiver presente, caso contrário, retorna `False`.

### Assinatura

```python
def teste(cls, codigo: str) -> bool:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos` e a lista de códigos. |
| `codigo` | `str` | Código a ser verificado na lista interna da classe. |

### Retorno

**Tipo:** `bool`

Indica se o código está presente na lista de códigos da classe (`True`) ou não (`False`).

### Dependências

- `{'nome': '_codigos', 'categoria': 'método interno', 'descricao': 'Método interno da classe que retorna a lista de códigos.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def teste(cls, codigo: str) -> bool:
        return codigo in cls._codigos()
```

</details>

---

<a id="funcao-103"></a>

## descricao_por_codigo

Retorna a descrição correspondente ao código fornecido.

Busca e retorna a descrição associada ao código no mapa interno da classe. Retorna `None` se o código não for encontrado.

### Assinatura

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método e o mapa de descrições. |
| `codigo` | `str` | Código para o qual a descrição é buscada. |

### Retorno

**Tipo:** `str | None`

Descrição correspondente ao código ou `None` se não encontrado.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método interno da classe que retorna o mapa de descrições.'}`
- `{'nome': 'get', 'categoria': 'chamada', 'descricao': 'Método do dicionário que busca a chave especificada.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def descricao_por_codigo(cls, codigo: str) -> str | None:
        return cls._mapa().get(codigo)
```

</details>

---

<a id="funcao-104"></a>

## _mapa

Retorna um dicionário mapeando códigos para descrições de métodos.

A função verifica se o atributo `_cache` existe na classe. Se não existir, ele é criado a partir dos métodos da classe, onde a chave é o código do método e o valor é sua descrição. Caso contrário, retorna o dicionário já existente.

### Assinatura

```python
def _mapa(cls) -> dict[str, str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém os métodos a serem mapeados. |

### Retorno

**Tipo:** `dict[str, str]`

Dicionário onde as chaves são códigos de métodos e os valores são suas descrições.

### Dependências

- `hasattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _mapa(cls) -> dict[str, str]:
        if not hasattr(cls, "_cache"):
            cls._cache = {m.codigo: m.descricao for m in cls}
        return cls._cache
```

</details>

---

<a id="funcao-105"></a>

## _codigos

Retorna um conjunto de chaves do mapa interno da classe.

A função retorna um conjunto contendo todas as chaves presentes no mapa interno da classe. O mapa é obtido através do método `_mapa()` da própria classe.

### Assinatura

```python
def _codigos(cls) -> set[str]:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método `_codigos`. |

### Retorno

**Tipo:** `set[str]`

Conjunto de chaves do mapa interno da classe.

### Dependências

- `{'nome': 'cls._mapa', 'categoria': 'chamada', 'descricao': 'Método que retorna o mapa interno da classe.'}`
- `{'nome': 'keys', 'categoria': 'chamada', 'descricao': 'Método do dicionário que retorna as chaves.'}`
- `{'nome': 'set', 'categoria': 'chamada', 'descricao': 'Função que cria um conjunto a partir de uma sequência.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _codigos(cls) -> set[str]:
        return set(cls._mapa().keys())
```

</details>

---

<a id="funcao-106"></a>

## validar_datas

Valida um valor utilizando uma função de validação específica.

Esta função utiliza um decorador para validar um valor. O valor é passado para a função `validar_data` que realiza a validação propriamente dita.

### Assinatura

```python
def validar_datas(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde o método está sendo definido. |
| `valor` | `Não especificado` | Valor a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_datas(cls, valor):
        return validar_data(valor)
```

</details>

---

<a id="funcao-107"></a>

## validar_data_opcional

Valida um valor opcional como uma data.

A função valida se o valor é uma data, permitindo que seja vazio. Utiliza outra função interna para realizar a validação propriamente dita.

### Assinatura

```python
def validar_data_opcional(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em métodos de classe). |
| `valor` | `Não especificado` | Valor a ser validado, que pode ser uma data ou vazio. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_data_opcional(cls, valor):
        return validar_data(valor, vazio=True)
```

</details>

---

<a id="funcao-108"></a>

## validar_decimais_positivos

Valida se um valor é decimal e positivo.

Utiliza uma validação de campo para garantir que o valor seja um número decimal e positivo. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_decimais_positivos(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a validação é aplicada. |
| `valor` | `Não especificado` | Valor a ser validado como decimal positivo. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_decimais_positivos(cls, valor):
        return validar_decimal(valor, min_val=0)
```

</details>

---

<a id="funcao-109"></a>

## validar_decimais

Valida se um valor é decimal.

Utiliza uma validação de campo para verificar se o valor fornecido é decimal. A função delega a verificação ao método `validar_decimal`.

### Assinatura

```python
def validar_decimais(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_decimais(cls, valor):
        return validar_decimal(valor)
```

</details>

---

<a id="funcao-110"></a>

## validar_projeto_origem

Valida um valor como decimal, permitindo valores vazios e com mínimo zero.

A função valida se o valor é um número decimal válido, aceitando tanto valores numéricos quanto strings que representem números decimais. Também permite que o valor seja vazio (None) ou seja igual a zero.

### Assinatura

```python
def validar_projeto_origem(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a validação está sendo aplicada. |
| `valor` | `Não especificado` | Valor a ser validado como decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que pode ser um número ou None.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_projeto_origem(cls, valor):
        return validar_decimal(valor, vazio=True, min_val=0)
```

</details>

---

<a id="funcao-111"></a>

## validar_percentuais

Valida se um valor é um percentual válido.

Verifica se o valor está dentro do intervalo de 0 a 1, permitindo valores vazios. Utiliza uma função auxiliar para realizar a validação decimal.

### Assinatura

```python
def validar_percentuais(cls, valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado como percentual. |

### Retorno

**Tipo:** `Não especificado`

O valor original, se válido. Caso contrário, lança uma exceção de validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_percentuais(cls, valor):
        return validar_decimal(
            valor, vazio=True, min_val=0, max_val=1
        )
```

</details>

---

<a id="funcao-112"></a>

## validar_atributos

Valida um atributo para garantir que ele seja um inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um inteiro e se está dentro do intervalo definido por min_val e max_val. Utiliza uma validação interna chamada 'validar_inteiro'.

### Assinatura

```python
def validar_atributos(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se a validação for bem-sucedida; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_atributos(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=99
        )
```

</details>

---

<a id="funcao-113"></a>

## validar_flag

Valida se um valor é uma flag booleana (0 ou 1).

A função valida que o valor fornecido está entre 0 e 1, inclusos. Utiliza a função `validar_inteiro` para realizar a validação.

### Assinatura

```python
def validar_flag(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado, deve estar entre 0 e 1. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_inteiro` após a validação.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_flag(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=1
        )
```

</details>

---

<a id="funcao-114"></a>

## validar_tipo_oe

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido esteja entre 0 e 8, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro.

### Assinatura

```python
def validar_tipo_oe(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em métodos de classe). |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, geralmente fornecido automaticamente pelo Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se estiver dentro do intervalo especificado.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tipo_oe(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0, max_val=8
        )
```

</details>

---

<a id="funcao-115"></a>

## validar_inteiros_positivos

Valida se um valor é um inteiro positivo.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um inteiro e, em seguida, valida se ele é maior ou igual a zero (inteiro positivo).

### Assinatura

```python
def validar_inteiros_positivos(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_inteiros_positivos(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name, min_val=0
        )
```

</details>

---

<a id="funcao-116"></a>

## validar_aneel

Valida um valor conforme as regras definidas para o ANEEL.

A função valida se o valor fornecido está dentro do intervalo permitido pelo ANEEL, que é de 0 a 200.000.

### Assinatura

```python
def validar_aneel(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde o método está sendo definido. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele estiver dentro do intervalo permitido, caso contrário, lança uma exceção.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_aneel(cls, valor, info):
        return validar_inteiro(
            valor, info.field_name,
            min_val=0, max_val=200000,
        )
```

</details>

---

<a id="funcao-117"></a>

## validar_textos

Valida um texto com base em regras específicas.

A função valida o valor de um campo, permitindo que seja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna chamada `validar_texto` para realizar o processo de validação.

### Assinatura

```python
def validar_textos(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `valor` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_textos(cls, valor, info):
        return validar_texto(
            valor, info.field_name,
            vazio=True, max_len=1000,
        )
```

</details>

---

<a id="funcao-118"></a>

## validar_unidade

Valida um valor de unidade utilizando uma função de validação de texto.

A função valida o valor de unidade, limitando-o a uma máxima extensão de 10 caracteres. Utiliza uma função auxiliar para realizar a validação do texto.

### Assinatura

```python
def validar_unidade(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor da unidade a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor de unidade após a validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_unidade(cls, valor, info):
        return validar_texto(
            valor, info.field_name, max_len=10
        )
```

</details>

---

<a id="funcao-119"></a>

## validar_uar

Valida um valor conforme regras específicas para o domínio UAR, TUC e UC.

A função valida se o valor fornecido pertence ao conjunto de domínios 'UAR', 'TUC' ou 'UC'. Utiliza uma validação adicional definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_uar(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_texto` após a validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_uar(cls, valor, info):
        return validar_texto(
            valor, info.field_name,
            max_len=3,
            dominio=["UAR", "TUC", "UC"],
        )
```

</details>

---

<a id="funcao-120"></a>

## validar_codigos

Valida um código de acordo com regras específicas.

A função valida o valor fornecido, considerando se é vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_codigos(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O resultado da validação, que é retornado pela função 'validar_texto'.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Método de validador de campo do Pydantic.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_codigos(cls, valor, info):
        return validar_texto(
                                valor,
                                info.field_name,
                                vazio=info.field_name == "Cd_NT",
                                max_len=25,
                            )
```

</details>

---

<a id="funcao-121"></a>

## validar_cc

Valida se um valor é um código de cliente (CC) válido.

Verifica se o valor fornecido é um código de cliente (CC) dentro do domínio permitido. Utiliza uma função auxiliar para validar a integridade do valor e outra para verificar se ele pertence ao conjunto de valores válidos.

### Assinatura

```python
def validar_cc(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado como código de cliente. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, provavelmente fornecidas pelo framework de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não faz parte do domínio de CC.

### Dependências

- `pydantic.field_validator`
- `ValoresCC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cc(cls, valor, info):
        num = validar_inteiro(valor, info.field_name)

        if not ValoresCC.teste(valor):
            raise ValueError(
                f"{valor} não faz parte do domínio de CC."
            )

        return valor
```

</details>

---

<a id="funcao-122"></a>

## validar_tuc

Valida um valor como código de UC (Unidade Curricular).

Verifica se o valor fornecido é um número inteiro entre 99 e 999, e se atende aos critérios específicos definidos pela classe ValoresTUC. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_tuc(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado, provavelmente provenientes de um contexto de validação de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tuc(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=99, max_val=999,
        )

        if num not in (None, ""):
            if not ValoresTUC.teste(int(num)):
                raise ValueError(
                    "O dado não é válido como código de UC."
                )

        return valor
```

</details>

---

<a id="funcao-123"></a>

## validar_ti

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_ti(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original, caso seja válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`
- `ValoresTI.teste`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ti(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=1, max_val=100,
        )

        if num not in (None, ""):
            if not ValoresTI.teste(int(num)):
                raise ValueError(
                    "O dado não é válido como TI."
                )

        return valor
```

</details>

---

<a id="funcao-124"></a>

## validar_ti_origem

Valida um valor como TI de origem.

Verifica se o valor fornecido é válido como TI de origem, considerando que pode ser vazio. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_ti_origem(cls, valor, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em métodos de validação de modelos Pydantic). |
| `valor` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, geralmente fornecido automaticamente pelo Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI de origem.

### Dependências

- `pydantic.field_validator`
- `ValoresTI.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ti_origem(cls, valor, info):
        num = validar_inteiro(
            valor, info.field_name,
            min_val=1, max_val=100,
            vazio=True,
        )

        if num in (None, "", " "):
            return valor

        if not ValoresTI.teste(int(num)):
            raise ValueError(
                f"O dado '{num}' não é válido como TI de origem."
            )

        return valor
```

</details>

---

<a id="funcao-125"></a>

## capturar_erros_estrutura

Captura erros estruturados durante a validação de dados.

Executa um handler para processar os valores e captura quaisquer erros de validação que ocorram. Se houver erros, cria um objeto da classe atual com os dados fornecidos e armazena os erros de validação nesse objeto.

### Assinatura

```python
def capturar_erros_estrutura(cls, valores: Any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual que contém o método. |
| `valores` | `Any` | Valores a serem validados e processados pelo handler. |
| `handler` | `Não especificado` | Função ou método que realiza o processamento dos valores. |

### Retorno

**Tipo:** `Não especificado`

Objeto da classe atual com os dados e erros de validação, se houver.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução do handler.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def capturar_erros_estrutura(cls, valores: Any, handler):
        try:
            return handler(valores)

        except ValidationError as exc:
            dados = (
                valores
                if isinstance(valores, dict)
                else valores.__dict__
            )

            obj = cls.model_construct(**dados)
            obj._erros_registro = exc.errors(
                include_url=False
            )

            return obj
```

</details>

---

<a id="funcao-126"></a>

## pipeline_validacao_completa

Executa um pipeline de validação completo para uma tabela de objetos.

Este método itera sobre cada objeto na tabela, coleta erros estruturais e aplica regras de negócios. Se houver erros, lança uma exceção de validação. Caso contrário, retorna a instância atual do objeto.

### Assinatura

```python
def pipeline_validacao_completa(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |

### Retorno

**Tipo:** `Não especificado`

A instância atual do objeto após a validação completa.

### Exceções

- **`pydantic.ValidationError`**: Quando ocorrem erros de validação durante o processo.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pipeline_validacao_completa(self):
        erros = []

        for indice, obj in enumerate(self.tabela):
            linha_id = getattr(
                obj, "Ide_AIS", None
            ) or f"Linha_{indice + 1}"

            campos_invalidos = self._coletar_erros_estrutura(
                obj=obj,
                indice=indice,
                erros=erros,
            )

            self._executar_regras_negocio(
                obj=obj,
                indice=indice,
                linha_id=linha_id,
                campos_invalidos=campos_invalidos,
                erros=erros,
            )

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros,
            )

        return self
```

</details>

---

<a id="funcao-127"></a>

## _coletar_erros_estrutura

Coleta os campos inválidos de um objeto AIS e adiciona mensagens de erro a uma lista.

Esta função percorre os erros registrados em um objeto AIS, identifica os campos inválidos e adiciona mensagens de erro formatadas à lista fornecida. Os erros são armazenados como conjuntos de strings para evitar duplicatas.

### Assinatura

```python
# Consulte o código-fonte de _coletar_erros_estrutura
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `obj` | `AIS` | Objeto AIS que contém os erros a serem coletados. |
| `indice` | `int` | Índice utilizado para localização dos erros na tabela. |
| `erros` | `list` | Lista onde as mensagens de erro formatadas serão adicionadas. |

### Retorno

**Tipo:** `set[str]`

Conjunto contendo os nomes dos campos inválidos encontrados no objeto AIS.

### Dependências

- `{'nome': 'ValueError', 'categoria': 'chamada', 'descricao': 'Exceção utilizada para criar mensagens de erro formatadas.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _coletar_erros_estrutura(
                                        *,
                                        obj: AIS,
                                        indice: int,
                                        erros: list,
                                    ) -> set[str]:

        campos_invalidos = set()

        for erro in obj._erros_registro:
            loc = erro.get("loc", ())
            loc = (loc,) if isinstance(loc, str) else tuple(loc)

            if loc and isinstance(loc[0], str):
                campos_invalidos.add(loc[0])

            mensagem = f"[Estrutura] {erro.get('msg', '')}"

            erros.append({
                "type": "value_error",
                "loc": ("tabela", indice) + loc,
                "input": erro.get("input"),
                "ctx": {
                    "error": ValueError(mensagem),
                },
            })

        return campos_invalidos
```

</details>

---

<a id="funcao-128"></a>

## _executar_regras_negocio

Executa regras de negócios em um objeto AIS.

Aplica uma série de funções de validação a um objeto AIS, considerando campos inválidos e armazenando erros encontrados. Cada regra é verificada para garantir que não haja interseção entre os campos inválidos e as dependências da regra antes de serem executadas.

### Assinatura

```python
# Consulte o código-fonte de _executar_regras_negocio
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o método. |
| `obj` | `AIS` | Objeto AIS a ser validado. |
| `indice` | `int` | Índice do objeto na coleção de objetos sendo validados. |
| `linha_id` | `Não especificado` | Identificador da linha associada ao objeto AIS. |
| `campos_invalidos` | `set[str]` | Conjunto de campos que já foram identificados como inválidos. |
| `erros` | `list` | Lista onde erros encontrados durante a validação serão armazenados. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor.

### Dependências

- `{'nome': 'campos_invalidos.intersection', 'categoria': 'chamada', 'descricao': 'Verifica a interseção entre os campos inválidos e as dependências de cada regra.'}`
- `{'nome': 'self._executar_regra', 'categoria': 'chamada', 'descricao': 'Executa uma função de validação específica, passando os argumentos necessários.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _executar_regras_negocio(
                                    self, 
                                    *,
                                    obj: AIS,
                                    indice: int,
                                    linha_id,
                                    campos_invalidos: set[str],
                                    erros: list,
                                ) -> None:

        regras = [
            (
                validar_tuc_ti,
                "Nr_TUC",
                ("Nr_TUC", "Nr_TI", "Nr_A1"),
                (obj.Nr_TUC, obj.Nr_TI, linha_id, obj.Nr_A1),
            ),
            (
                validar_tucs_proibidos,
                "Nr_TUC",
                ("Nr_TUC",),
                (obj.Nr_TUC, linha_id),
            ),
            (
                validar_administracao,
                "Cd_CC",
                ("Nr_TI", "Cd_CC"),
                (obj.Nr_TI, obj.Cd_CC, linha_id),
            ),
            (
                validar_cm,
                "Nr_CM",
                ("Nr_TI", "Nr_CM"),
                (obj.Nr_TI, obj.Nr_CM, linha_id),
            ),
            (
                validar_ti_distribuicao,
                "Nr_TI",
                ("Nr_TI",),
                (obj.Nr_TI, linha_id),
            ),
            (
                validar_cabos,
                "Nr_TUC",
                (
                    "Nr_TUC", "Nr_A1", "Nr_A3",
                    "Nr_A4", "Nr_A5", "Cd_UND_AIS",
                ),
                (
                    obj.Nr_TUC, obj.Nr_A1, obj.Nr_A3,
                    obj.Nr_A4, obj.Nr_A5,
                    obj.Cd_UND_AIS, linha_id,
                ),
            ),
            (
                validar_torre_poste,
                "Nr_TI",
                ("Nr_TI", "Nr_TUC", "Nr_A1"),
                (obj.Nr_TI, obj.Nr_TUC, obj.Nr_A1, linha_id),
            ),
            (
                validar_FLG_PER,
                "FLG_PER",
                ("Dt_Imob", "FLG_PER"),
                (obj.Dt_Imob, obj.FLG_PER, linha_id),
            ),
            (
                validar_bem_individual,
                "Nr_TUC",
                (
                    "Nr_TI", "Nr_TUC",
                    "Nr_A1", "Nr_A2", "Nr_A3",
                    "Nr_A4", "Nr_A5", "Nr_A6",
                    "Qtd_AIS", "Cd_UAR",
                ),
                (
                    obj.Nr_TI, obj.Nr_TUC,
                    obj.Nr_A1, obj.Nr_A2, obj.Nr_A3,
                    obj.Nr_A4, obj.Nr_A5, obj.Nr_A6,
                    obj.Qtd_AIS, linha_id, obj.Cd_UAR,
                ),
            ),
        ]

        for func, campo, dependencias, args in regras:
            if campos_invalidos.intersection(dependencias):
                continue

            self._executar_regra(
                                    func=func,
                                    campo=campo,
                                    args=args,
                                    obj=obj,
                                    indice=indice,
                                    linha_id=linha_id,
                                    erros=erros,
                                )
```

</details>

---

<a id="funcao-129"></a>

## _executar_regra

Executa uma regra de negócio e captura quaisquer erros que possam ocorrer.

Esta função executa uma função fornecida como argumento (`func`) com os argumentos especificados (`args`). Se a função levantar um `ValueError`, o erro é capturado e registrado em uma lista de erros. O registro inclui detalhes sobre o tipo de erro, a localização do erro (tabela, índice, campo), o valor de entrada que causou o erro e o contexto do erro.

### Assinatura

```python
# Consulte o código-fonte de _executar_regra
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `func` | `Callable` | Função a ser executada como parte da regra de negócio. |
| `campo` | `str` | Nome do campo relacionado ao erro. |
| `args` | `tuple` | Argumentos a serem passados para a função `func`. |
| `obj` | `AIS` | Objeto que contém os dados relevantes para a regra de negócio. |
| `indice` | `int` | Índice da linha relacionada ao erro. |
| `linha_id` | `Não especificado` | ID da linha que causou o erro (se aplicável). |
| `erros` | `list` | Lista onde os erros serão registrados. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Exceções

- **`ValueError`**: Quando a função `func` levanta um `ValueError`, o erro é capturado e registrado em `erros`.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def _executar_regra(
                            *,
                            func: Callable,
                            campo: str,
                            args: tuple,
                            obj: AIS,
                            indice: int,
                            linha_id,
                            erros: list,
                        ) -> None:

        try:
            func(*args)

        except ValueError as exc:
            mensagem = (
                            f"[Regra Negocio] "
                            f"[ID: {linha_id}] {exc}"
                        )

            erros.append({
                            "type": "value_error",
                            "loc": ("tabela", indice, campo),
                            "input": getattr(obj, campo, None),
                            "ctx": {
                                "error": ValueError(mensagem),
                            },
                        })
```

</details>

---

<a id="funcao-130"></a>

## validar_TI

Valida se um valor é uma TI (Tipo de Identificação) válida.

A função valida se o valor fornecido é um número inteiro entre 1 e 100, inclusive, e se ele passa na validação específica para TI utilizando a classe ValoresTI. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é um número inteiro entre 1 e 100 ou não passa na validação específica para TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if not ValoresTI.teste(int(num)):
            raise ValueError(f'O valor {value!r} não é válido como TI.\n')
        return value
```

</details>

---

<a id="funcao-131"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor fornecido é válido, considerando que não pode estar vazio e tem um comprimento máximo de 255 caracteres.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic em que o validador está sendo definido. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
```

</details>

---

<a id="funcao-132"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-133"></a>

## _decimal_br

Converte um valor em uma instância de Decimal, adaptando formatos brasileiros.

A função aceita valores numéricos (inteiros ou floats) e strings representando números, normalizando-os para o formato Decimal. Se a string contiver vírgula como separador decimal, ela é convertida para ponto antes da conversão.

### Assinatura

```python
def _decimal_br(value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `value` | `Não especificado` | Valor a ser convertido em Decimal. Pode ser um número inteiro, float ou string. |

### Retorno

**Tipo:** `Decimal`

Instância de Decimal representando o valor normalizado.

### Dependências

- `decimal.Decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _decimal_br(value):
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        texto = str(value).strip()
        if ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        return Decimal(texto)
```

</details>

---

<a id="funcao-134"></a>

## validar_consistencia_valores

Valida a consistência dos valores em um objeto.

Verifica se os valores totais correspondem à soma dos componentes e se não há inconsistências entre campos relacionados. Lança uma exceção de validação caso encontre erros.

### Assinatura

```python
def validar_consistencia_valores(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os valores a serem validados. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atual se não houver erros de validação. Caso contrário, lança uma exceção de validação.

### Exceções

- **`ValidationError`**: Quando encontrados erros de consistência nos valores.

### Dependências

- `decimal.Decimal`
- `pydantic.ValidationError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_consistencia_valores(self):
        valores = {}
        for campo in (*self.COMPONENTES_ROA, 'VL_TOT_ROA',
                      *self.COMPONENTES_FISC, 'VL_TOT_FISC'):
            try:
                valores[campo] = self._decimal_br(getattr(self, campo))
            except (InvalidOperation, TypeError, ValueError):
                return self

        erros = []

        def adicionar(campo, mensagem):
            erros.append({
                            'type': 'value_error',
                            'loc': (campo,),
                            'input': getattr(self, campo),
                            'ctx': {'error': ValueError(mensagem)},
                        })

        for componentes, total, rotulo in (
                                                (self.COMPONENTES_ROA, 'VL_TOT_ROA', 'ROA'),
                                                (self.COMPONENTES_FISC, 'VL_TOT_FISC', 'FISC'),
                                            ):
            soma = sum((valores[c] for c in componentes), Decimal('0'))
            if abs(valores[total] - soma) > self.TOLERANCIA:
                adicionar(
                            total,
                            f'{total} ({valores[total]:.2f}) difere da soma dos '
                            f'componentes {rotulo} ({soma:.2f}).'
                        )
        pares = zip(
                        (*self.COMPONENTES_FISC, 'VL_TOT_FISC'),
                        (*self.COMPONENTES_ROA, 'VL_TOT_ROA'),
                    )
        for campo_fisc, campo_roa in pares:
            if valores[campo_fisc] > valores[campo_roa] + self.TOLERANCIA:
                adicionar(
                            campo_fisc,
                            f'{campo_fisc} ({valores[campo_fisc]:.2f}) não pode ser '
                            f'maior que {campo_roa} ({valores[campo_roa]:.2f}).'
                        )

        if erros:
            raise ValidationError.from_exception_data('ROSV', erros)
        return self
```

</details>

---

<a id="funcao-135"></a>

## validar_ide

Valida se um valor é um inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-136"></a>

## validar_ide1

Valida um valor como inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um inteiro e se está dentro do intervalo definido por min_val e max_val. Também permite que o valor seja vazio, conforme especificado pelo parâmetro vazio.

### Assinatura

```python
def validar_ide1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=8, vazio=True)
```

</details>

---

<a id="funcao-137"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor fornecido é válido, considerando que não pode estar vazio e tem um comprimento máximo de 25 caracteres.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic em que o validador está sendo usado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=25)
```

</details>

---

<a id="funcao-138"></a>

## validar_cda

Valida um valor conforme as regras definidas para campos de texto.

A função valida o valor fornecido, garantindo que não esteja vazio e que seu comprimento não exceda 255 caracteres. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_cda(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cda(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
```

</details>

---

<a id="funcao-139"></a>

## validar_cdd

Valida um valor conforme as regras definidas para campos de texto em um modelo Pydantic.

Esta função é usada como um validador de campo em modelos Pydantic. Ela verifica se o valor fornecido atende aos critérios de validação especificados, incluindo a permissão de valores vazios e uma restrição máxima de comprimento de caracteres.

### Assinatura

```python
def validar_cdd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cdd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
```

</details>

---

<a id="funcao-140"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'field_validator', 'categoria': 'chamada'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-141"></a>

## validar_Dt

Valida uma data, permitindo valores vazios.

Esta função valida se o valor fornecido é uma data válida. Ela aceita tanto datas como valores vazios, conforme especificado pelo parâmetro `vazio=True` na chamada à função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma data. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-142"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

A função valida se o valor é um número decimal válido, considerando um mínimo e permitindo valores vazios.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0, vazio=True)
```

</details>

---

<a id="funcao-143"></a>

## validar_vl_pct

Valida se um valor é uma porcentagem decimal.

Verifica se o valor fornecido é uma porcentagem decimal, permitindo valores vazios e aceitando valores mínimos de zero.

### Assinatura

```python
def validar_vl_pct(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como porcentagem decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for uma porcentagem decimal.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_pct(cls, value):
        return validar_decimal(value, vazio=True, min_val=0)
```

</details>

---

<a id="funcao-144"></a>

## validar_tipo_obra

Valida se o valor de um campo específico é um inteiro dentro de um intervalo definido.

A função valida que o valor fornecido para um campo específico seja um número inteiro, aceitando valores vazios. O intervalo permitido vai de 1 a 12.

### Assinatura

```python
def validar_tipo_obra(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tipo_obra(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12, vazio=True)
```

</details>

---

<a id="funcao-145"></a>

## validar_nr_fas

Valida se um valor é um número de fases válido.

Verifica se o valor fornecido está entre 1 e 3, permitindo valores vazios.

### Assinatura

```python
def validar_nr_fas(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3, vazio=True)
```

</details>

---

<a id="funcao-146"></a>

## validar_ide

Valida se um valor é um inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-147"></a>

## validar_ide1

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está contido no intervalo definido por min_val e max_val. Se a validação falhar, uma exceção será lançada.

### Assinatura

```python
def validar_ide1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=8)
```

</details>

---

<a id="funcao-148"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor fornecido é válido, considerando que não pode estar vazio e tem um comprimento máximo de 25 caracteres.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic em que o validador está sendo usado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=25)
```

</details>

---

<a id="funcao-149"></a>

## validar_cda

Valida um valor conforme as regras definidas para campos de texto.

A função valida o valor fornecido, garantindo que não esteja vazio e que seu comprimento não exceda 255 caracteres. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_cda(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cda(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
```

</details>

---

<a id="funcao-150"></a>

## validar_cdd

Valida um valor conforme as regras definidas para campos de texto em um modelo Pydantic.

Esta função é usada como um validador de campo em modelos Pydantic. Ela verifica se o valor fornecido atende aos critérios de validação especificados, incluindo a permissão de valores vazios e uma restrição máxima de comprimento de caracteres.

### Assinatura

```python
def validar_cdd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cdd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
```

</details>

---

<a id="funcao-151"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'field_validator', 'categoria': 'chamada'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-152"></a>

## validar_Dt

Valida uma data, permitindo valores vazios.

Esta função valida se o valor fornecido é uma data válida. Ela aceita tanto datas como valores vazios, conforme especificado pelo parâmetro `vazio=True` na chamada à função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma data. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-153"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

A função valida se o valor é um número decimal válido, considerando um mínimo e permitindo valores vazios.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0, vazio=True)
```

</details>

---

<a id="funcao-154"></a>

## validar_vl_pct

Valida se um valor é uma porcentagem decimal.

Verifica se o valor fornecido é uma porcentagem decimal, permitindo valores vazios e aceitando valores mínimos de zero.

### Assinatura

```python
def validar_vl_pct(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como porcentagem decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for uma porcentagem decimal.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_pct(cls, value):
        return validar_decimal(value, vazio=True, min_val=0)
```

</details>

---

<a id="funcao-155"></a>

## validar_tipo_obra

Valida se o valor de um campo específico é um inteiro dentro de um intervalo definido.

A função valida que o valor fornecido para um campo específico é um número inteiro e está dentro do intervalo de 1 a 12, inclusivo. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_tipo_obra(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tipo_obra(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12)
```

</details>

---

<a id="funcao-156"></a>

## validar_nr_fas

Valida se um valor é um número de fases válido.

Verifica se o valor fornecido está entre 1 e 3, permitindo valores vazios.

### Assinatura

```python
def validar_nr_fas(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3, vazio=True)
```

</details>

---

<a id="funcao-157"></a>

## verifica_dados

Verifica os dados fornecidos e corrige possíveis erros de validação.

A função verifica se as datas 'Dt_Inic_Proj', 'Dt_Energ' e 'Dt_Uniti' estão em ordem cronológica correta. Se houver erros de validação, a função corrige os valores padrão para '1920-01-01'. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem verificados e corrigidos. |
| `handler` | `Não especificado` | Função de validação dos dados. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos dados, com possíveis correções.

### Exceções

- **`ValueError`**: Quando uma data está mais recente que outra na sequência cronológica.

### Dependências

- `datetime.date`
- `datetime.datetime`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        def to_date(v):
            if not v or str(v).strip() == "":
                return date(1920, 1, 1)
            try:
                return datetime.strptime(str(v).strip(), "%Y/%m/%d").date()
            except Exception:
                return date(1920, 1, 1)

        D1 = to_date(result.Dt_Inic_Proj)
        D2 = to_date(result.Dt_Energ)
        D3 = to_date(result.Dt_Uniti)

        linha = getattr(result, "Ide_RO_Sintetico", "")

        if D1 > D2:
            raise ValueError(f"Dt_Ini_Proj (linha {linha}) é mais recente que Dt_Energ.\n")
        if D1 > D3:
            raise ValueError(f"Dt_Ini_Proj (linha {linha}) é mais recente que Dt_Uniti.\n")
        if D2 > D3:
            raise ValueError(f"Dt_Energ (linha {linha}) é mais recente que Dt_Uniti.\n")

        if validation_error is not None:
            raise validation_error
        
        return result
```

</details>

---

<a id="funcao-158"></a>

## validar_cds

Valida um valor de acordo com regras específicas para campos de texto.

A função valida se o valor fornecido é uma string não vazia e tem no máximo 255 caracteres. Utiliza a função `validar_texto` internamente para realizar as verificações.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'tipo': 'chamada_interna'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
```

</details>

---

<a id="funcao-159"></a>

## validar_flg_dir

Valida se o valor é uma flag booleana (0 ou 1).

Verifica se o valor fornecido é `None` ou uma string vazia e, em caso contrário, valida se ele está entre 0 e 1.

### Assinatura

```python
def validar_flg_dir(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou `None` se for inválido.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_flg_dir(cls, value, info):
        if value is None or str(value).strip() == "":
            return None
        return validar_inteiro(
                                    value,
                                    info.field_name,
                                    min_val=0,
                                    max_val=1
                                )
```

</details>

---

<a id="funcao-160"></a>

## validar_vl_cda

Valida se um valor está dentro de um intervalo específico, permitindo valores vazios.

A função valida que o valor fornecido esteja entre 0 e 10, incluindo esses limites. Também permite que o valor seja vazio.

### Assinatura

```python
def validar_vl_cda(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou None se for vazio.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cda(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=10, vazio=True)
```

</details>

---

<a id="funcao-161"></a>

## validar_cnpj

Valida um CNPJ utilizando uma função auxiliar.

Esta função utiliza um validador de CNPJ para verificar a validade do valor fornecido. A verificação é realizada por meio de uma chamada à função `validar_CNPJ`.

### Assinatura

```python
def validar_cnpj(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_CNPJ`, que indica se o CNPJ é válido ou não.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpj(cls, value):
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-162"></a>

## validar_vl_cdng

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 7, inclusive. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
```

</details>

---

<a id="funcao-163"></a>

## validar_vl_cdca

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido seja um número inteiro e esteja dentro do intervalo definido por min_val (inclusivo) e max_val (inclusivo). Permite valores vazios conforme especificado.

### Assinatura

```python
def validar_vl_cdca(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
```

</details>

---

<a id="funcao-164"></a>

## validar_vl_voc

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. É usada como um decorador em classes Pydantic para garantir a integridade dos dados.

### Assinatura

```python
def validar_vl_voc(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o validador. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, levanta uma exceção de validação.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_voc(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-165"></a>

## validar_TUC

Valida se um valor é válido como código de UC (Unidade Curricular).

A função valida que o valor seja um número inteiro entre 1 e 1000, e que atenda a uma condição específica definida pela classe ValoresTUC. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usada em métodos de validação de modelos Pydantic). |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado (geralmente fornecido automaticamente pelo Pydantic). |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou None caso contrário.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=1000)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-166"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
```

</details>

---

<a id="funcao-167"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-168"></a>

## validar_nr_a1

Valida um valor como um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida se o valor fornecido é um número inteiro dentro do intervalo de 0 a 99. Permite que o valor seja vazio (None). Utiliza uma validação interna chamada 'validar_inteiro'.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-169"></a>

## validar_ide

Valida se um valor é um inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-170"></a>

## validar_Txt_N

Valida um valor de texto conforme regras específicas.

A função valida se o valor é uma string vazia ou não e verifica seu comprimento máximo. Utiliza a função `validar_texto` para realizar as validações.

### Assinatura

```python
def validar_Txt_N(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, esperado ser uma string. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
```

</details>

---

<a id="funcao-171"></a>

## validar_und

Valida um valor de acordo com regras específicas para uma unidade.

A função valida o valor fornecido, considerando se está vazio e limitando sua comprimento máximo. Utiliza a função `validar_texto` internamente para realizar a validação.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada_interna'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
```

</details>

---

<a id="funcao-172"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-173"></a>

## validar_FLGa

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção.

### Assinatura

```python
def validar_FLGa(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLGa(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=3)
```

</details>

---

<a id="funcao-174"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo é válido, considerando parâmetros como permitir valores vazios e definindo uma máxima comprimento.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
```

</details>

---

<a id="funcao-175"></a>

## validar_cd1

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 25 caracteres.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-176"></a>

## validar_cd2

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo atende aos critérios especificados, incluindo uma restrição de comprimento máximo de 255 caracteres.

### Assinatura

```python
def validar_cd2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-177"></a>

## validar_cd21

Valida um valor conforme regras específicas para CD21.

Esta função valida um valor utilizando uma validação de texto, permitindo valores vazios e limitando a sua extensão máxima em 255 caracteres. Ela é usada como um decorador de campo em esquemas Pydantic.

### Assinatura

```python
def validar_cd21(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd21(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
```

</details>

---

<a id="funcao-178"></a>

## validar_desc

Valida uma descrição de acordo com regras específicas.

A função valida se a descrição fornecida é um texto válido, permitindo que seja vazia e limitando seu comprimento máximo em 1000 caracteres. Utiliza outra função chamada `validar_texto` para realizar o processo de validação.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, neste caso, uma descrição. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-179"></a>

## verifica_dados

Verifica os dados fornecidos e adiciona erros se necessário.

A função verifica a validade dos dados utilizando um manipulador de dados e adiciona erros em caso de problemas. Os erros são armazenados e, no final, uma exceção `ValidationError` é lançada se houver erros.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Dados a serem verificados. |
| `handler` | `Não especificado` | Função que processa os dados e pode lançar uma exceção `ValidationError`. |

### Retorno

**Tipo:** `Não especificado`

O resultado do manipulador de dados, ou lança uma exceção `ValidationError` se houver erros.

### Exceções

- **`pydantic.ValidationError`**: Quando há erros na validação dos dados.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        erros = []
        try:
            result = handler(values)
        except ValidationError as exc:
            erros.extend(
                            {
                                "type": erro["type"],
                                "loc": tuple(erro["loc"]),
                                "input": erro.get("input"),
                                **(
                                    {"ctx": erro["ctx"]}
                                    if "ctx" in erro
                                    else {}
                                )
                            }
                            for erro in exc.errors()
                        )


            result = cls.model_construct(**values)

        def obter(campo, padrao=None):
            return getattr(result, campo, padrao)

        def esta_vazio(valor):
            return (
                        valor is None
                        or (
                            isinstance(valor, str)
                            and valor.strip() == ""
                        )
                    )

        def adicionar_erro(campo, mensagem, valor=None):
            erros.append({
                            "type": "value_error",
                            "loc": (campo,),
                            "input": valor,
                            "ctx": {
                                "error": ValueError(mensagem)
                            }
                        })

        def converter_decimal(valor, campo):
            if esta_vazio(valor):
                return 0.0

            try:
                return float(
                                str(valor).strip().replace(",", ".")
                            )

            except (TypeError, ValueError):
                adicionar_erro(
                                    campo,
                                    f"Valor decimal inválido: {valor!r}",
                                    valor
                                )
                return None

        nr_ti = obter("Nr_TI")
        nr_tuc = obter("Nr_TUC")
        nr_a1 = obter("Nr_A1")
        nr_a3 = obter("Nr_A3")

        nr_atributos = [
                            obter(f"Nr_A{i}")
                            for i in range(1, 7)
                        ]

        cd_ca = obter("Cd_CA")
        cd_ng = obter("Cd_NG")
        flg_oat = obter("FLG_OAT")
        cd_atip = obter("Cd_ATIP")
        cod_item = obter("COD_ITEM")

        unidade = str(
                        obter("Unidade", "") or ""
                    ).strip().lower()

        qtd = converter_decimal(
                                    obter("Qtd"),
                                    "Qtd"
                                )

        vl_tot = converter_decimal(
                                        obter("VL_tot"),
                                        "VL_tot"
                                    )


        try:
            validar_ti_distribuicao(
                                        nr_ti,
                                        obter("Ide_RO_Analitico", "")
                                    )

        except ValueError as exc:
            adicionar_erro(
                                "Nr_TI",
                                str(exc),
                                nr_ti
                            )

        if qtd is not None and vl_tot is not None:
            if qtd * vl_tot < 0:
                adicionar_erro(
                                    "VL_tot",
                                    (
                                        "Sinal divergente entre "
                                        f"quantidade ({qtd}) "
                                        f"e valor ({vl_tot})."
                                    ),
                                    obter("VL_tot")
                                )

        if (
                str(nr_tuc) == "190"
                and str(nr_a1) in {"1", "2"}
            ):
            unidades_esperadas = (
                                    {"kg"}
                                    if str(nr_a3) == "1"
                                    else {"m", "mt"}
                                )

            if unidade not in unidades_esperadas:
                adicionar_erro(
                                    "Unidade",
                                    (
                                        "Unidade incompatível com "
                                        "a classificação TUC. "
                                        f"Esperado: {', '.join(sorted(unidades_esperadas))}."
                                    ),
                                    obter("Unidade")
                                )

        if (
                str(cd_ng) in {"3", "4"}
                and esta_vazio(cd_ca)
            ):
            adicionar_erro(
                            "Cd_CA",
                            (
                                "Cd_CA deve ser preenchido "
                                f"quando Cd_NG é {cd_ng}."
                            ),
                            cd_ca
                        )

        if (
                str(cd_ng) in {"1", "2", "4"}
                and esta_vazio(cod_item)
            ):
            adicionar_erro(
                                "COD_ITEM",
                                (
                                    "COD_ITEM deve ser preenchido "
                                    f"quando Cd_NG é {cd_ng}."
                                ),
                                cod_item
                            )

        if str(flg_oat) == "0":

            if str(cd_atip or "0").strip() != "0":
                adicionar_erro(
                                    "Cd_ATIP",
                                    (
                                        "Cd_ATIP deve ser zero "
                                        "quando FLG_OAT é 0."
                                    ),
                                    cd_atip
                                )

        elif str(flg_oat) == "1":

            try:
                cd_atip_int = int(
                                        str(cd_atip).strip()
                                    )
            except (TypeError, ValueError):
                cd_atip_int = None

            if cd_atip_int not in range(1, 11):
                adicionar_erro(
                                    "Cd_ATIP",
                                    (
                                        "Cd_ATIP deve estar entre "
                                        "1 e 10 quando FLG_OAT é 1."
                                    ),
                                    cd_atip
                                )

        tucagem_incompleta = (
                                esta_vazio(nr_tuc)
                                or any(
                                    esta_vazio(atributo)
                                    for atributo in nr_atributos
                                )
                            )

        if (
                str(cd_ng) == "1"
                and tucagem_incompleta
            ):
            campos_tucagem = [
                                "Nr_TUC",
                                "Nr_A1",
                                "Nr_A2",
                                "Nr_A3",
                                "Nr_A4",
                                "Nr_A5",
                                "Nr_A6"
                            ]

            for campo in campos_tucagem:
                valor = obter(campo)

                if esta_vazio(valor):
                    adicionar_erro(
                                        campo,
                                        (
                                            "Tucagem obrigatória "
                                            "quando Cd_NG é 1."
                                        ),
                                        valor
                                    )

        if erros:
            raise ValidationError.from_exception_data(
                                                        cls.__name__,
                                                        erros
                                                    )

        return result
```

</details>

---

<a id="funcao-180"></a>

## validar_vl_cda

Valida se um valor está dentro de um intervalo específico, permitindo valores vazios.

A função valida que o valor fornecido esteja entre 0 e 10, incluindo esses limites. Também permite que o valor seja vazio.

### Assinatura

```python
def validar_vl_cda(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, conforme a função `validar_inteiro`.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cda(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=10, vazio=True)
```

</details>

---

<a id="funcao-181"></a>

## validar_cnpj

Valida um CNPJ utilizando uma função auxiliar.

Esta função utiliza um validador de CNPJ para verificar a validade do valor fornecido. A implementação específica da validação está em 'validar_CNPJ'.

### Assinatura

```python
def validar_cnpj(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação do CNPJ.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_CNPJ', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpj(cls, value):
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-182"></a>

## validar_vl_cdng

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 7, inclusive. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
```

</details>

---

<a id="funcao-183"></a>

## validar_vl_cdca

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 6, incluindo esses valores. Também permite que o valor seja vazio.

### Assinatura

```python
def validar_vl_cdca(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
```

</details>

---

<a id="funcao-184"></a>

## validar_vl_voc

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. A verificação é realizada por meio de uma chamada a outra função de validação.

### Assinatura

```python
def validar_vl_voc(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. A função não especifica um tipo de retorno explícito.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_voc(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-185"></a>

## validar_TUC

Valida um valor como código de Unidade Curricular (UC).

Verifica se o valor fornecido é válido como código de UC, considerando que deve ser um número inteiro entre 1 e 1000 e passar em uma validação específica definida pela classe ValoresTUC.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, provavelmente fornecidas pelo framework Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou None se não for válido.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=1000)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-186"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor válido após a validação.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
```

</details>

---

<a id="funcao-187"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-188"></a>

## validar_nr_a1

Valida um valor como um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida se o valor fornecido é um número inteiro dentro do intervalo de 0 a 99. Permite que o valor seja vazio (None). Utiliza uma validação interna chamada 'validar_inteiro'.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-189"></a>

## validar_ide

Valida se um valor é um inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-190"></a>

## validar_Txt_N

Valida um valor de texto conforme regras específicas.

A função valida se o valor é uma string vazia ou não e verifica seu comprimento máximo. Utiliza a função `validar_texto` para realizar as validações.

### Assinatura

```python
def validar_Txt_N(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser uma string. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
```

</details>

---

<a id="funcao-191"></a>

## validar_und

Valida um valor de acordo com regras específicas para unidades.

A função valida o valor fornecido, considerando se está vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
```

</details>

---

<a id="funcao-192"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-193"></a>

## validar_FLGa

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um número inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção.

### Assinatura

```python
def validar_FLGa(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLGa(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=3)
```

</details>

---

<a id="funcao-194"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo é válido, considerando parâmetros como permitir valores vazios e definindo uma máxima comprimento.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o validador. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
```

</details>

---

<a id="funcao-195"></a>

## validar_cd1

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 25 caracteres.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-196"></a>

## validar_cd2

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo atende aos critérios de validação, limitando-o a uma máxima comprimento de 255 caracteres.

### Assinatura

```python
def validar_cd2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-197"></a>

## validar_cd21

Valida um valor conforme regras específicas para CD21.

Esta função valida um valor utilizando uma validação de texto, permitindo valores vazios e limitando a sua extensão máxima em 255 caracteres. Ela é usada como um decorador de validação em classes Pydantic.

### Assinatura

```python
def validar_cd21(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd21(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
```

</details>

---

<a id="funcao-198"></a>

## validar_desc

Valida uma descrição de acordo com regras específicas.

A função valida se a descrição fornecida é um texto válido, permitindo que esteja vazia e limitando seu comprimento máximo em 1000 caracteres. Utiliza outra função chamada `validar_texto` para realizar o processo de validação.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, neste caso, uma descrição. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-199"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-200"></a>

## validar_cnpj

Valida um CNPJ utilizando uma função auxiliar.

Esta função utiliza um validador de CNPJ para verificar a validade do valor fornecido. A implementação específica da validação está em 'validar_CNPJ'.

### Assinatura

```python
def validar_cnpj(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação do CNPJ.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_CNPJ', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpj(cls, value):
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-201"></a>

## validar_vl_cdng

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido seja um número inteiro e esteja dentro do intervalo definido por min_val (inclusivo) e max_val (inclusivo). Também permite valores vazios, conforme indicado pelo parâmetro vazio.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro dentro do intervalo especificado. Caso contrário, uma exceção pode ser levantada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=7)
```

</details>

---

<a id="funcao-202"></a>

## validar_vl_cdca

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 6, incluindo esses valores. Também permite que o valor seja vazio.

### Assinatura

```python
def validar_vl_cdca(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdca(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=6)
```

</details>

---

<a id="funcao-203"></a>

## validar_vl_voc

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. A verificação é realizada por meio de uma chamada a outra função de validação.

### Assinatura

```python
def validar_vl_voc(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. A função não especifica um tipo de retorno explícito.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_voc(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-204"></a>

## validar_TUC

Valida se um valor é um código de Unidade Curricular (UC) válido.

A função valida que o valor seja um número inteiro entre 100 e 999, inclusive. Além disso, verifica se o valor atende aos critérios específicos definidos pela classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente um número inteiro representando um código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado, provavelmente fornecido pelo framework Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é um código de UC válido.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if  (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-205"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor válido após a validação, ou None se o valor for vazio e permitido.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`
- `ValoresTI.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
```

</details>

---

<a id="funcao-206"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-207"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida que o valor fornecido seja um número inteiro dentro do intervalo de 0 a 99. Também permite que o valor esteja vazio, conforme especificado pelo parâmetro `vazio`.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
```

</details>

---

<a id="funcao-208"></a>

## validar_ide

Valida se um valor é um inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-209"></a>

## validar_Txt_N

Valida um valor de texto conforme regras específicas.

A função valida se o valor é uma string vazia ou não e verifica seu comprimento máximo. Utiliza a função `validar_texto` para realizar as validações.

### Assinatura

```python
def validar_Txt_N(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser uma string. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Txt_N(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
```

</details>

---

<a id="funcao-210"></a>

## validar_und

Valida um valor de acordo com regras específicas para unidades.

A função valida o valor fornecido, considerando se está vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=10)
```

</details>

---

<a id="funcao-211"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-212"></a>

## validar_cd2

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo atende aos critérios especificados, incluindo uma máxima comprimento e permitindo valores vazios.

### Assinatura

```python
def validar_cd2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-213"></a>

## validar_cd1

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 255 caracteres.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-214"></a>

## validar_desc

Valida uma descrição de acordo com regras específicas.

A função valida se a descrição fornecida é um texto válido, permitindo que esteja vazia e limitando seu comprimento máximo em 1000 caracteres. Utiliza outra função chamada `validar_texto` para realizar o processo de validação.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, neste caso, uma descrição. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-215"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-216"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-217"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-218"></a>

## validar_desc

Valida uma descrição, garantindo que ela não exceda um comprimento máximo.

Esta função é usada para validar a descrição de um campo em um esquema Pydantic. Ela chama outra função `validar_texto` para realizar o validação propriamente dita, limitando o comprimento da descrição a 1000 caracteres.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor da descrição a ser validada. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-219"></a>

## validar_depara

Valida um valor de acordo com regras específicas para deparação.

A função valida o valor fornecido utilizando uma validação de texto, permitindo valores vazios e limitando a sua comprimento máximo em 25 caracteres. Esta função é usada como um decorador de validação em classes Pydantic.

### Assinatura

```python
def validar_depara(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_depara(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-220"></a>

## validar_FC

Valida um valor utilizando uma função de validação decimal.

A função utiliza um validador decimal para verificar se o valor é válido, permitindo que o valor esteja vazio.

### Assinatura

```python
def validar_FC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a validação está sendo aplicada. |
| `value` | `Não especificado` | Valor que será validado. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função de validação decimal.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FC(cls, value):
        return validar_decimal(value, vazio=True)
```

</details>

---

<a id="funcao-221"></a>

## validar_FLG_AGR

Valida se um valor é um inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Lança uma exceção caso contrário.

### Assinatura

```python
def validar_FLG_AGR(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG_AGR(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=False, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-222"></a>

## validar_Cd_Nm

Valida um valor como um número inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um número inteiro e se está dentro do intervalo definido por min_val (inclusivo) e max_val (inclusivo). Permite que o valor seja vazio, conforme especificado.

### Assinatura

```python
def validar_Cd_Nm(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, conforme retornado pela função `validar_inteiro`.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Cd_Nm(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=23)
```

</details>

---

<a id="funcao-223"></a>

## validar_Cd_Nm1

Valida um valor como inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um número inteiro e se ele está dentro do intervalo definido por min_val e max_val. O parâmetro vazio permite que valores vazios sejam considerados válidos.

### Assinatura

```python
def validar_Cd_Nm1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Cd_Nm1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=33)
```

</details>

---

<a id="funcao-224"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-225"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-226"></a>

## validar_cd1

Valida um valor de acordo com regras específicas para campos de texto.

A função valida o valor fornecido, verificando se ele é uma string e se seu comprimento não excede 255 caracteres. Também permite que o campo seja vazio.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255, vazio=True)
```

</details>

---

<a id="funcao-227"></a>

## validar_Cd_Nm

Valida um valor como um número inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um número inteiro e se está dentro do intervalo definido por min_val e max_val. O parâmetro vazio permite que valores vazios sejam considerados válidos.

### Assinatura

```python
def validar_Cd_Nm(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Cd_Nm(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=33)
```

</details>

---

<a id="funcao-228"></a>

## validar_desc

Valida uma descrição, garantindo que ela não exceda um comprimento máximo.

Esta função é usada para validar a descrição de um campo em um esquema Pydantic. Ela chama outra função `validar_texto` para realizar o validação propriamente dita, limitando o comprimento da descrição a 1000 caracteres.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor da descrição a ser validada. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-229"></a>

## validar_Cd_Nm1

Valida um valor como inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um número inteiro e se ele está dentro do intervalo definido por min_val e max_val. O parâmetro vazio permite que valores vazios sejam considerados válidos.

### Assinatura

```python
def validar_Cd_Nm1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção é levantada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Cd_Nm1(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True, min_val=1, max_val=11)
```

</details>

---

<a id="funcao-230"></a>

## validar_FC

Valida um valor utilizando uma função de validação decimal.

A função utiliza um validador decimal para verificar se o valor é válido, permitindo que o valor esteja vazio.

### Assinatura

```python
def validar_FC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a validação está sendo aplicada. |
| `value` | `Não especificado` | Valor que será validado. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função de validação decimal.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FC(cls, value):
        return validar_decimal(value, vazio=True)
```

</details>

---

<a id="funcao-231"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-232"></a>

## validar_und

Valida um valor de acordo com regras específicas para uma unidade.

A função valida o valor fornecido utilizando a função `validar_texto`, limitando-o a uma máxima extensão de 10 caracteres. O nome do campo é passado para fins de contexto na validação.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-233"></a>

## validar_fat

Valida se um valor é um decimal e se está acima de zero.

A função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_fat(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde o método está sendo definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_fat(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-234"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-235"></a>

## validar_Hr

Valida se um valor é uma string representando uma hora no formato HH:MM:SS.

Verifica se o valor fornecido é uma string que representa uma hora válida no formato de horas, minutos e segundos (HH:MM:SS). Caso contrário, lança exceções específicas para diferentes tipos de erros.

### Assinatura

```python
def validar_Hr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, esperado ser uma string representando uma hora. |

### Retorno

**Tipo:** `Não especificado`

Retorna o valor original se ele for válido. Caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor é None ou uma string vazia.
- **`ValueError`**: Quando a string não tem exatamente 8 caracteres.
- **`ValueError`**: Quando a string não está no formato HH:MM:SS.
- **`ValueError`**: Quando o valor não é do tipo esperado (não é uma string).

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'importação', 'descricao': 'Método de validação do Pydantic.'}`
- `{'nome': 're.match', 'categoria': 'chamada', 'descricao': 'Função para verificar se uma string corresponde a um padrão regular.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Hr(cls, value):
        if isinstance(value, str):
            if (value is None) or (value == ''):
                raise ValueError(f'Não pode estar vazio.\n')
            if len(value) != 8:
                raise ValueError(f'O dado deve ter 8 caracteres.\n')
            if not re.match(r'^\d{2}:\d{2}:\d{2}$', value):
                raise ValueError(f'A data deve estar no formato HH:MM:SS.\n')
            return value
        else:
            raise ValueError(f"O valor não é do tipo esperado.\n")
```

</details>

---

<a id="funcao-236"></a>

## validar_cd3

Valida um valor conforme regras específicas para o campo CD3.

Esta função valida um valor utilizando uma validação de texto, limitando a sua comprimento máximo em 255 caracteres. Ela é usada como um decorador de validação em classes Pydantic.

### Assinatura

```python
def validar_cd3(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd3(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-237"></a>

## validar_cd

Valida se um valor é uma string dentro de um conjunto específico de domínios e com comprimento máximo.

A função valida que o valor fornecido seja uma string, esteja dentro do domínio especificado (LEVE, MÉDIA, PESADA, VIVA) e tenha no máximo 25 caracteres. Utiliza a função `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_cd(cls, value,info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value,info):
        return validar_texto(value, info.field_name, max_len=25, dominio = ['LEVE','MÉDIA','PESADA','VIVA'])
```

</details>

---

<a id="funcao-238"></a>

## validar_cd1

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 50 caracteres.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
```

</details>

---

<a id="funcao-239"></a>

## validar_cd2

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo é válido, considerando um comprimento máximo de 1000 caracteres e permitindo valores vazios.

### Assinatura

```python
def validar_cd2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
```

</details>

---

<a id="funcao-240"></a>

## validar_desc

Valida uma descrição, garantindo que ela não exceda um comprimento máximo.

Esta função é usada para validar a descrição de um campo em um esquema Pydantic. Ela chama outra função `validar_texto` para realizar o validação propriamente dita, limitando o comprimento da descrição a 1000 caracteres.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor da descrição a ser validada. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-241"></a>

## validar_frini

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido está entre 1 e 4, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro.

### Assinatura

```python
def validar_frini(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_frini(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=4)
```

</details>

---

<a id="funcao-242"></a>

## validar_cnpj

Valida um CNPJ utilizando uma função auxiliar.

Esta função utiliza um validador de CNPJ para verificar a validade do valor fornecido. A implementação específica da validação está em 'validar_CNPJ'.

### Assinatura

```python
def validar_cnpj(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação do CNPJ.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_CNPJ', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpj(cls, value):
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-243"></a>

## validar_serie

Valida se um valor é uma série de números inteiros dentro de um intervalo específico.

A função valida que o valor fornecido é um número inteiro e está dentro do intervalo definido por min_val e max_val. Também permite valores vazios, conforme indicado pelo parâmetro vazio.

### Assinatura

```python
def validar_serie(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=999999, vazio=True)
```

</details>

---

<a id="funcao-244"></a>

## validar_nr

Valida se um valor é um número inteiro.

A função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro, permitindo que o valor esteja vazio.

### Assinatura

```python
def validar_nr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True)
```

</details>

---

<a id="funcao-245"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor válido após a validação, ou None se o valor for vazio e permitido.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`
- `ValoresTI.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
```

</details>

---

<a id="funcao-246"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-247"></a>

## validar_FLG

Valida um valor como decimal, garantindo que ele seja maior ou igual a zero.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se está dentro do intervalo definido pelo parâmetro `min_val`, que neste caso é zero. Se o valor não for válido, uma exceção será lançada.

### Assinatura

```python
def validar_FLG(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém este validador. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-248"></a>

## validar_und

Valida um valor de acordo com regras específicas para uma unidade.

A função valida o valor fornecido utilizando a função `validar_texto`, limitando-o a uma máxima extensão de 10 caracteres. O nome do campo é passado para fins de contexto na validação.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-249"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-250"></a>

## validar_TUC

Valida um valor como código de Unidade Curricular (UC).

Verifica se o valor fornecido é válido como código de UC, considerando que deve ser um número inteiro entre 100 e 999, e que atenda a uma condição específica definida pela classe ValoresTUC.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente no código). |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, geralmente fornecido pelo framework Pydantic. |

### Retorno

**Tipo:** `Não especificado`

Valor validado ou None se não for válido.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if (nm != None) and (nm != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-251"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida que o valor fornecido seja um número inteiro dentro do intervalo de 0 a 99. Também permite que o valor esteja vazio, conforme especificado pelo parâmetro `vazio`.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
```

</details>

---

<a id="funcao-252"></a>

## validar_ide

Valida um valor como inteiro, permitindo valores vazios.

A função valida se o valor fornecido é um número inteiro. Ela aceita valores vazios conforme especificado pelo parâmetro `vazio=True` no chamado à função `validar_inteiro`. Esta validação é realizada através de um decorador `field_validator` do Pydantic.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como inteiro. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name,  vazio=True)
```

</details>

---

<a id="funcao-253"></a>

## validar_cd

Valida se um valor é um inteiro e maior ou igual a 1.

A função valida que o valor fornecido é um número inteiro e verifica se ele é maior ou igual a 1. Utiliza uma validação interna chamada 'validar_inteiro'.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-254"></a>

## validar_desc

Valida uma descrição de acordo com regras específicas.

A função valida se a descrição fornecida atende aos critérios estabelecidos, utilizando um validador de texto específico para verificar o comprimento máximo.

### Assinatura

```python
def validar_desc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da descrição a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_desc(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-255"></a>

## validar_depara

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir este critério.

### Assinatura

```python
def validar_depara(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_depara(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-256"></a>

## validar_FC

Valida um valor utilizando uma função de validação específica.

Esta função utiliza um decorador para validar um valor chamando outra função de validação chamada 'validar_data'. Ela é usada como um método de classe, o que sugere que pode ser parte de uma classe Pydantic ou semelhante.

### Assinatura

```python
def validar_FC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém este método. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função 'validar_data'.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Decorador usado para validar campos em classes Pydantic.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FC(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-257"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-258"></a>

## validar_cd

Valida um valor de CD utilizando uma função de texto.

Esta função valida um valor de CD chamando outra função `validar_texto`, verificando se o valor não excede a largura máxima de 25 caracteres. O nome do campo é passado para fins de contexto na validação.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 25)
```

</details>

---

<a id="funcao-259"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-260"></a>

## validar_nr_fas

Valida se um valor é um número de fases válido.

Verifica se o valor fornecido está entre 1 e 3, inclusos. Utiliza uma validação de inteiro personalizada para realizar a verificação.

### Assinatura

```python
def validar_nr_fas(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_fas(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-261"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-262"></a>

## validar_cd

Valida um valor de CD (Código Doméstico) em relação a regras específicas.

A função valida se o valor fornecido é uma string não nula, tem comprimento máximo de 50 caracteres e pertence à lista de domínio definida pela classe `ValoresNmVAR`. Caso contrário, lança um erro de validação.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a regra de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor validado, se for válido. Caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é uma string, tem comprimento maior que 50 caracteres ou não pertence à lista de domínio definida pela classe `ValoresNmVAR`.

### Dependências

- `pydantic.field_validator`
- `ValoresNmVAR.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_texto(value, info.field_name, max_len = 50)
        if (nm != None) and (nm != None) and (not ValoresNmVAR.teste(value)):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-263"></a>

## validar_FLG

Valida um valor como decimal, garantindo que ele seja maior ou igual a zero.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se está dentro do intervalo definido pelo parâmetro `min_val`, que neste caso é zero. Se o valor não for válido, uma exceção será lançada.

### Assinatura

```python
def validar_FLG(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém este validador. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-264"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-265"></a>

## validar_cd

Valida se um valor é um número inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um número inteiro e está dentro do intervalo definido por min_val (inclusivo) e max_val (inclusivo). Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=14)
```

</details>

---

<a id="funcao-266"></a>

## validar_us

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_us(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor original, se válido. Caso contrário, uma exceção de validação é lançada.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_us(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-267"></a>

## validar_ano

Valida se o valor é um ano válido.

Verifica se o valor fornecido é um número inteiro e se está dentro do intervalo mínimo de 2000. Utiliza uma validação interna para garantir que o valor seja um inteiro.

### Assinatura

```python
def validar_ano(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente no código) |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, geralmente não utilizado diretamente no código |

### Retorno

**Tipo:** `Não especificado`

O valor validado (se for válido), ou lança uma exceção se não for.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ano(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val = 2000)
```

</details>

---

<a id="funcao-268"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. A implementação específica da validação é realizada pela função `validar_decimal`.

### Assinatura

```python
def validar_vl(cls, v):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, v):
       return validar_decimal(v)
```

</details>

---

<a id="funcao-269"></a>

## validar_dt

Valida uma data utilizando um validador específico.

Esta função é usada para validar uma data chamando outro validador chamado 'validar_data'. Ela não realiza nenhuma operação adicional além de delegar a validação à função 'validar_data'.

### Assinatura

```python
def validar_dt(cls, v):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado, presumivelmente uma data. |

### Dependências

- `pydantic.field_validator`
- `validar_data`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_dt(cls, v):
       return validar_data(v)
```

</details>

---

<a id="funcao-270"></a>

## validar_tp

Valida um valor de texto em relação a um conjunto de domínios específicos.

A função valida se o valor fornecido pertence a uma lista predefinida de domínios. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_tp(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tp(cls, v, info):
       return validar_texto(v, info.field_name, dominio=["Outros","PLPT","IR","CCC","Tx_MED_AMORT"])
```

</details>

---

<a id="funcao-271"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
       return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-272"></a>

## validar_cd

Valida um valor conforme regras específicas.

A função valida se o valor fornecido é um inteiro válido e pertence a uma lista de domínio definida pela classe ValoresCCOE. Caso contrário, lança um ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor validado, se for um inteiro válido e pertencer à lista de domínio. Caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é um inteiro válido ou não pertence à lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name, vazio=True)
        if (nm != '') and (nm != None) and (not ValoresCCOE.teste(value)):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo, desconsiderar caso seja linha de Tx_MED_AMORT.\n")
        return nm
```

</details>

---

<a id="funcao-273"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta um `ValueError` com uma mensagem concatenada. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Função de manipulação que realiza a validação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(
                                        exclude={'Id_OE_MOV', 'Cd_CC', 'TP_OE', 'VL_SLD_INI', 'VL_SLD_REAV', 'Dt_REF', None}
                                    )
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))
        if validation_error is not None:
            raise validation_error
        return result
```

</details>

---

<a id="funcao-274"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-275"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-276"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-277"></a>

## validar_us

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_us(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que este método está sendo chamado. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_us(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-278"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-279"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-280"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-281"></a>

## validar_us

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_us(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que este método está sendo chamado. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_us(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-282"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-283"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-284"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-285"></a>

## validar_us

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_us(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que este método está sendo chamado. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_us(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-286"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-287"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-288"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-289"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção `ValueError` com uma mensagem concatenada dos erros. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Função de manipulação que realiza a validação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-290"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-291"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-292"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção com uma mensagem concatenada. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Manipulador de validação que processa os valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-293"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-294"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-295"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção `ValueError` com uma mensagem concatenada dos erros. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Função de manipulação que realiza a validação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-296"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-297"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-298"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção com uma mensagem concatenada. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Manipulador de validação que processa os valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-299"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-300"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-301"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção `ValueError` com uma mensagem concatenada dos erros. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Função de manipulação que realiza a validação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-302"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-303"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-304"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção com uma mensagem concatenada. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Manipulador de validação que processa os valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-305"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-306"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-307"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção `ValueError` com uma mensagem concatenada dos erros. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Função de manipulação que realiza a validação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_MOV', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-308"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-309"></a>

## validar_cd

Valida um valor de CD (Código de Diagnóstico) em um contexto específico.

Esta função valida se o valor fornecido é um código de diagnóstico válido e se pertence à lista de domínio definida pelo módulo ValoresCCOE. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de diagnóstico. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que é esperado ser um inteiro após a validação de integridade.

### Exceções

- **`ValueError`**: Quando o valor não faz parte da lista de domínio do campo.

### Dependências

- `pydantic.field_validator`
- `ValoresCCOE.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCCOE.teste(value):
            raise ValueError(f"{value} não faz parte da lista de domínio do campo.\n")
        return nm
```

</details>

---

<a id="funcao-310"></a>

## validar_vls

Valida os valores utilizando um manipulador e verifica erros adicionais.

A função valida os valores fornecidos usando o manipulador especificado. Se ocorrer uma exceção de validação, a função tenta construir um modelo com os valores fornecidos. Em seguida, verifica erros adicionais utilizando a função `anl_lcmt`. Se houver erros, levanta uma exceção com uma mensagem concatenada. Caso contrário, retorna o resultado da validação.

### Assinatura

```python
def validar_vls(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem validados. |
| `handler` | `Não especificado` | Manipulador de validação que processa os valores. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos valores.

### Exceções

- **`ValueError`**: Quando ocorrem erros adicionais durante a validação.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vls(cls, values, handler):
        validation_error = None

        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        valores = result.model_dump(exclude={'Id_OE_AMT', 'Cd_CC', None})
        erros = anl_lcmt(valores)
        if erros:
            raise ValueError("\n".join(erros))

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-311"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-312"></a>

## validar_cd

Valida um valor de CD utilizando uma função de validação de texto.

A função valida o valor do campo 'CD' usando a função `validar_texto`, limitando-o a uma máxima extensão de 25 caracteres. A validação é realizada pelo decorador `field_validator` da biblioteca Pydantic.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo 'CD' a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-313"></a>

## validar_cstipi

Valida o valor de CST-IPITributo conforme regras específicas.

Verifica se o valor fornecido está dentro dos domínios permitidos para CST-IPITributo, que são valores numéricos e strings específicos. Utiliza uma função auxiliar para realizar a validação do texto.

### Assinatura

```python
def validar_cstipi(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente no código) |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado (mesmo que não seja explicitamente retornado)

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cstipi(cls, value, info):
        return validar_texto(value, info.field_name, max_len=2, dominio=['00','01','02','03','04','05',
                                                                         '0','1','2','3','4','5','49',
                                                                  '50','51','52','53','54','55','99'])
```

</details>

---

<a id="funcao-314"></a>

## validar_csticms

Valida um valor de CST-ICMS (Código de Situação Tributária do ICMS) em um contexto específico.

A função valida se o valor fornecido é uma string que corresponde a um código válido de CST-ICMS, conforme definido no domínio especificado. Utiliza uma validação adicional para garantir que o valor seja uma string e tenha no máximo três caracteres.

### Assinatura

```python
def validar_csticms(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic em que a validação está sendo aplicada. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma string representando um código de CST-ICMS. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado, provavelmente fornecido pelo Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, levanta uma exceção de validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Método do Pydantic usado para definir um validador de campo.'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada', 'descricao': 'Função auxiliar que realiza a validação adicional dos valores de texto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_csticms(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio=['0','10','30','40','41','50','51','60','70','90',
                                                                  '101','102','103','201','202','203','300','400','500','900',
                                                                  '100','200','300','400','500','600','700','800',
                                                                  '110','210','310','410','510','610','710','810',
                                                                  '120','220','320','420','520','620','720','820',
                                                                  '130','230','330','430','530','630','730','830',
                                                                  '140','240','340','440','540','640','740','840',
                                                                  '141','241','341','441','541','641','741','841',
                                                                  '150','250','350','450','550','650','750','850',
                                                                  '151','251','351','451','551','651','751','851',
                                                                  '260','360','460','560','760','860','270','370',
                                                                  '470','570','770','870','190','290','390','490',
                                                                  '590','690','790','890'])
```

</details>

---

<a id="funcao-315"></a>

## validar_cdp

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, especificamente verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 255 caracteres.

### Assinatura

```python
def validar_cdp(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cdp(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-316"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-317"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'validar_inteiro', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-318"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar se o valor fornecido é válido. A implementação específica da validação decimal está contida na função `validar_decimal`.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. A função `validar_decimal` deve retornar o valor validado ou levantar uma exceção caso não seja válido.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-319"></a>

## validar_vl_odc

Valida um valor de ODC (Orçamento Detalhado de Contas) utilizando uma validação decimal.

A função verifica se o valor fornecido é nulo ou uma string vazia, retornando `None` em caso afirmativo. Caso contrário, chama a função `validar_decimal` para realizar a validação do valor.

### Assinatura

```python
def validar_vl_odc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, geralmente um número ou uma string representando um número. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, não utilizado diretamente na função. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou `None` se for inválido.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_odc(cls, value, info):

        if value is None or str(value).strip() == "":
            return None

        return validar_decimal(value)
```

</details>

---

<a id="funcao-320"></a>

## validar_al

Valida um valor como decimal dentro de um intervalo específico.

A função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se está dentro do intervalo definido por min_val e max_val. Se o valor for inválido, uma exceção será lançada.

### Assinatura

```python
def validar_al(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_al(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-321"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-322"></a>

## validar_vl_cdng

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 7, inclusive. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=7)
```

</details>

---

<a id="funcao-323"></a>

## validar_und

Valida um valor de acordo com regras específicas para uma unidade.

A função valida o valor fornecido utilizando a função `validar_texto`, limitando-o a uma máxima extensão de 10 caracteres. O nome do campo é passado para fins de contexto na validação.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-324"></a>

## validar_cfop

Valida um valor CFOP (Código Fiscal de Operações e Prestações) utilizando regras específicas.

A função valida se o valor fornecido é um CFOP válido conforme as regras estabelecidas em ValoresCFOP.teste. Caso contrário, lança uma exceção ValueError informando que o CFOP é inválido e deve ser verificado na SEFAZ.

### Assinatura

```python
def validar_cfop(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado como CFOP. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

Valor validado como CFOP, após a conversão para inteiro.

### Exceções

- **`ValueError`**: Quando o valor não é um CFOP válido conforme as regras da SEFAZ.

### Dependências

- `pydantic.field_validator`
- `ValoresCFOP.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cfop(cls, value, info):
        nm = validar_inteiro(value, info.field_name)
        if not ValoresCFOP.teste(value):
            raise ValueError(f"CFOP inválido, verifique se é válido na SEFAZ.\n")
        return nm
```

</details>

---

<a id="funcao-325"></a>

## validar_ncm

Valida se o valor é um número inteiro.

Utiliza uma validação de campo para garantir que o valor fornecido seja um número inteiro. A função `validar_inteiro` é chamada internamente para realizar a verificação.

### Assinatura

```python
def validar_ncm(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ncm(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-326"></a>

## validar_extipi

Valida se um valor é um inteiro válido de acordo com as regras definidas em `validar_inteiro`.

Esta função utiliza o decorador `@field_validator` do Pydantic para validar um valor como um inteiro. O valor é considerado válido se for maior ou igual a zero e permitir valores vazios, conforme especificado na chamada à função `validar_inteiro`.

### Assinatura

```python
def validar_extipi(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_extipi(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, vazio=True)
```

</details>

---

<a id="funcao-327"></a>

## validar_cnpk

Valida um valor como CNPK (CNPJ ou CPF).

Verifica se o valor é válido como CNPJ. Se for um CPF, lança uma exceção informando que deve ser um CNPJ.

### Assinatura

```python
def validar_cnpk(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Exceções

- **`ValueError`**: Quando o valor contém 11 dígitos, indicando que é um CPF em vez de um CNPJ.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpk(cls, value):
        numero = digitos(value)

        if len(numero) == 11:
            raise ValueError(
                                "O campo CNPJ_Forn contém 11 dígitos, "
                                "quantidade correspondente a um CPF. "
                                "Verifique se foi informado um CPF em vez de um CNPJ e se está correto."
                            )
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-328"></a>

## validar_serie

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido está entre 1 e 1000000, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro válido.

### Assinatura

```python
def validar_serie(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=1000000)
```

</details>

---

<a id="funcao-329"></a>

## validar_nr

Valida se um valor é um número inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_nr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-330"></a>

## validar_NFe

Valida uma chave de Nota Fiscal Eletrônica (NFe).

Verifica se a chave fornecida é válida, aceitando apenas dígitos e rejeitando valores vazios ou não-ASCII.

### Assinatura

```python
def validar_NFe(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma chave NFe. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

A chave NFe se for válida, ou uma string vazia se não for fornecido um valor válido.

### Exceções

- **`ValueError`**: Quando a chave contém caracteres não-ASCII ou não é composta apenas por dígitos.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NFe(cls, value, info):
        if value is None or str(value).strip() == "":
            return ""
        chave = str(value).strip()
        if not chave.isascii() or not chave.isdigit():
            raise ValueError("Cd_NFe deve conter somente dígitos.")
        return chave
```

</details>

---

<a id="funcao-331"></a>

## verifica_dados

Verifica a validade dos dados em um objeto.

Realiza uma série de verificações nos atributos do objeto, coletando erros e lançando uma exceção se houver problemas.

### Assinatura

```python
def verifica_dados(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os dados a serem verificados. |

### Retorno

**Tipo:** `Não especificado`

A instância atual (`self`) se não houver erros de validação.

### Exceções

- **`pydantic.ValidationError`**: Quando ocorrem erros de validação durante as verificações.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(self):
        erros = []
        self._validar_cfop(erros)
        self._validar_chave_nfe(erros)
        self._validar_flags(erros)
        self._validar_ipi(erros)
        self._validar_icms(erros)
        self._validar_valores(erros)
        self._validar_aliquotas(erros)

        if erros:
            raise ValidationError.from_exception_data(type(self).__name__, erros)
        return self
```

</details>

---

<a id="funcao-332"></a>

## _erro

Adiciona um erro personalizado à lista de erros.

Esta função adiciona um erro personalizado à lista de erros, associando-o a um campo específico e incluindo uma mensagem de erro.

### Assinatura

```python
def _erro(self, erros: list, campo: str, mensagem: str) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que chama o método. |
| `erros` | `list` | Lista onde os erros serão adicionados. |
| `campo` | `str` | Nome do campo associado ao erro. |
| `mensagem` | `str` | Mensagem de erro a ser adicionada. |

### Retorno

**Tipo:** `None`

Nenhum valor é retornado.

### Dependências

- `{'imports': ['pydantic_core.PydanticCustomError'], 'chamadas': ['PydanticCustomError', 'erros.append', 'getattr']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _erro(self, erros: list, campo: str, mensagem: str) -> None:
        erros.append({
                        "type": PydanticCustomError("regra_negocio", mensagem),
                        "loc": (campo,),
                        "input": getattr(self, campo, None),
                    })
```

</details>

---

<a id="funcao-333"></a>

## _texto

Converte um valor em uma string vazia se for `None`, caso contrário, retorna a representação de string do valor.

A função verifica se o valor é `None` e, se for, retorna uma string vazia. Caso contrário, converte o valor para sua representação de string usando a função interna `str()`. Esta função é útil para garantir que um valor sempre seja uma string, substituindo valores nulos por uma string vazia.

### Assinatura

```python
def _texto(valor) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser convertido em string. Se for `None`, será retornado uma string vazia. |

### Retorno

**Tipo:** `str`

Representação de string do valor, ou uma string vazia se o valor original era `None`.

### Dependências

- `str`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _texto(valor) -> str:
        return "" if valor is None else str(valor)
```

</details>

---

<a id="funcao-334"></a>

## _valor

Retorna o valor de um campo específico após conversão.

Acessa o valor de um atributo do objeto e aplica uma função de conversão flutuante a ele.

### Assinatura

```python
def _valor(self, campo: str):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém o campo. |
| `campo` | `str` | Nome do atributo cujo valor será retornado e convertido. |

### Retorno

**Tipo:** `Não especificado`

Valor do campo após conversão flutuante.

### Dependências

- `conv_flut`
- `getattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _valor(self, campo: str):
        return conv_flut(getattr(self, campo))
```

</details>

---

<a id="funcao-335"></a>

## _normalizar_numero

Normaliza um número removendo zeros à esquerda.

Converte o valor em uma string e remove zeros à esquerda. Se o valor for nulo, retorna '0'.

### Assinatura

```python
def _normalizar_numero(valor) -> str:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser normalizado. |

### Retorno

**Tipo:** `str`

String normalizada sem zeros à esquerda.

### Dependências

- `lstrip`
- `str`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _normalizar_numero(valor) -> str:
        return str(valor or "").lstrip("0") or "0"
```

</details>

---

<a id="funcao-336"></a>

## _validar_cfop

Valida o CFOP (Código Fiscal de Operações e Prestações) para garantir que seja um CFOP de entrada.

A função verifica se o CFOP começa com os dígitos '4', '5' ou '6', indicando uma operação de saída. Se for, registra um erro informando que é necessário um CFOP de entrada.

### Assinatura

```python
def _validar_cfop(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe. |
| `erros` | `list` | Lista onde os erros serão adicionados. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor.

### Dependências

- `{'nome': 'cfop.startswith', 'categoria': 'chamada', 'descricao': "Verifica se o CFOP começa com os dígitos '4', '5' ou '6'."}`
- `{'nome': 'self._erro', 'categoria': 'chamada', 'descricao': 'Registra um erro na lista de erros.'}`
- `{'nome': 'self._texto', 'categoria': 'chamada', 'descricao': 'Obtém o valor do CFOP como texto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_cfop(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        if cfop.startswith(("4", "5", "6")):
            self._erro(erros, "Cd_CFOP", "CFOP de saída ao invés de entrada")
```

</details>

---

<a id="funcao-337"></a>

## _validar_chave_nfe

Valida a chave de uma Nota Fiscal Eletrônica (NFe) e registra erros se houver problemas.

A função verifica se a chave da NFe é válida em termos de comprimento, campos específicos e data. Se encontrar qualquer problema, adiciona um erro à lista fornecida.

### Assinatura

```python
def _validar_chave_nfe(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os atributos necessários para a validação. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

A função não retorna nenhum valor. Os resultados são armazenados na lista de erros.

### Dependências

- `{'nome': 'data.strftime', 'categoria': 'chamada', 'descricao': 'Método para formatar datas em strings.'}`
- `{'nome': 'digitos', 'categoria': 'chamada', 'descricao': 'Função que extrai apenas os dígitos de uma string.'}`
- `{'nome': 'getattr', 'categoria': 'chamada', 'descricao': 'Método para obter o valor de um atributo de um objeto.'}`
- `{'nome': 'hasattr', 'categoria': 'chamada', 'descricao': 'Função que verifica se um objeto tem um determinado atributo.'}`
- `{'nome': 'len', 'categoria': 'chamada', 'descricao': 'Função para obter o comprimento de uma sequência.'}`
- `{'nome': 'self._erro', 'categoria': 'chamada', 'descricao': 'Método da instância que adiciona um erro à lista de erros.'}`
- `{'nome': 'self._normalizar_numero', 'categoria': 'chamada', 'descricao': 'Método da instância que normaliza um número para comparação.'}`
- `{'nome': 'self._texto', 'categoria': 'chamada', 'descricao': 'Método da instância que converte um objeto em uma string.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_chave_nfe(self, erros: list) -> None:
        chave = digitos(self.Cd_NFe)
        if not chave:
            return

        if len(chave) != 44:
            self._erro(erros, "Cd_NFe", "Chave da NFe deve possuir 44 dígitos")
            return 

        for campo, descricao, trecho in (
                                            ("CNPJ_Forn", "CNPJ", chave[6:20]),
                                            ("Nr_SerieNF", "Número de série", chave[22:25]),
                                            ("Nr_NF", "Número da NFe", chave[25:34]),
                                        ):
            informado = digitos(getattr(self, campo))
            if self._normalizar_numero(trecho) != self._normalizar_numero(informado):
                self._erro(erros, campo, f"{descricao} não confere com a chave da NFe")

        data = self.Dt_NF
        if hasattr(data, "strftime"):
            ano_mes = data.strftime("%y%m")
        else:
            texto = self._texto(data)
            if len(texto) < 7 or texto[4:5] != "-":
                self._erro(erros, "Dt_NF", "Data da NFe inválida para comparação com a chave")
                return
            ano_mes = texto[2:4] + texto[5:7]

        if chave[2:6] != ano_mes:
            self._erro(erros, "Dt_NF", "Data da NFe não confere com a chave da NFe")
```

</details>

---

<a id="funcao-338"></a>

## _validar_flags

Valida as flags e valores de uma nota fiscal.

Verifica se os valores das flags e campos específicos estão corretos, adicionando erros à lista fornecida caso contrário.

### Assinatura

```python
def _validar_flags(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os métodos e atributos necessários para a validação. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor.

### Dependências

- `{'nome': 'CFOPS_BPR', 'categoria': 'constante', 'descricao': 'Lista de CFOPs que devem ter o FLG_BPR definido.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_flags(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        flg_icms = self._texto(self.FLG_ICMS)
        flg_bpr = self._texto(self.FLG_BPR)
        flg_tpnf = self._texto(self.FLG_TPNF)
        qtd = self._valor("Qtd")
        vl_icms = self._valor("VL_TOT_ICMS")
        vl_difal = self._valor("VL_DIFAL")

        if flg_icms != "0" and vl_difal + vl_icms < 0.1:
            self._erro(erros, "FLG_ICMS", "Verifique o FLG_ICMS")
        if flg_bpr in {"0", ""} and cfop in CFOPS_BPR:
            self._erro(erros, "FLG_BPR", "Verifique o FLG_BPR")
        if flg_tpnf == "0" and qtd != 0:
            self._erro(erros, "Qtd", "Nota complementar com quantidade diferente de zero")
```

</details>

---

<a id="funcao-339"></a>

## _validar_ipi

Valida a CST_IPI e o valor total de IPI.

Verifica se a CST_IPI termina em '0' e se o valor total de IPI é diferente de zero. Caso contrário, adiciona um erro à lista de erros.

### Assinatura

```python
def _validar_ipi(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os métodos e atributos necessários para a validação. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor.

### Dependências

- `{'nome': 'cst_ipi.endswith', 'categoria': 'chamada', 'descricao': "Verifica se a string CST_IPI termina em '0'."}`
- `{'nome': 'self._erro', 'categoria': 'chamada', 'descricao': 'Adiciona um erro à lista de erros.'}`
- `{'nome': 'self._texto', 'categoria': 'chamada', 'descricao': 'Obtém o valor do atributo CST_IPI como uma string.'}`
- `{'nome': 'self._valor', 'categoria': 'chamada', 'descricao': 'Obtém o valor total de IPI.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_ipi(self, erros: list) -> None:
        cst_ipi = self._texto(self.CST_IPI)
        if not cst_ipi.endswith("0") and self._valor("VL_TOT_IPI") != 0:
            self._erro(erros, "VL_TOT_IPI", "Verificar CST_IPI ou VL_TOT_IPI — parece isento")
```

</details>

---

<a id="funcao-340"></a>

## _validar_icms

Valida os valores de ICMS, ST e DIFAL em relação à CST_ICMS.

Verifica se os valores de VL_TOT_ICMS, VL_ST e VL_DIFAL estão consistentes com a CST_ICMS. Lança erros caso as condições não sejam atendidas.

### Assinatura

```python
def _validar_icms(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os métodos e atributos utilizados. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor. Adiciona erros à lista fornecida se as condições não forem atendidas.

### Dependências

- `{'nome': 'CST_ICMS_COM_ICMS', 'categoria': 'constante', 'descricao': 'Lista de CST_ICMS que indicam a presença de ICMS.'}`
- `{'nome': 'CST_ICMS_COM_ST', 'categoria': 'constante', 'descricao': 'Lista de CST_ICMS que indicam a presença de ST.'}`
- `{'nome': 'CST_ICMS_COM_ICMS', 'categoria': 'constante', 'descricao': 'Lista de CST_ICMS que indicam a presença de DIFAL.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_icms(self, erros: list) -> None:
        cst_final = self._texto(self.CST_ICMS)[-2:]
        if cst_final not in CST_ICMS_COM_ICMS and self._valor("VL_TOT_ICMS") != 0:
            self._erro(erros, "VL_TOT_ICMS", "Verificar CST_ICMS ou VL_TOT_ICMS — não parece ter ICMS")
        if cst_final not in CST_ICMS_COM_ST and self._valor("VL_ST") != 0:
            self._erro(erros, "VL_ST", "Verificar CST_ICMS ou VL_ST — não parece ser ST")
        if cst_final not in CST_ICMS_COM_ICMS and self._valor("VL_DIFAL") != 0:
            self._erro(erros, "VL_DIFAL", "Verificar CST_ICMS ou VL_DIFAL — não parece ser DIFAL")
```

</details>

---

<a id="funcao-341"></a>

## _validar_valores

Valida os valores de acordo com regras específicas.

Verifica se os valores correspondem a certos critérios, adicionando erros à lista fornecida caso contrário. Os critérios incluem verificação do CFOP e dos valores de VL_DIFAL e VL_TOT_LIQ.

### Assinatura

```python
def _validar_valores(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os métodos e atributos necessários para a validação. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor. Os resultados são armazenados na lista de erros.

### Dependências

- `{'chamadas': ['abs', 'self._erro', 'self._texto', 'self._valor'], 'imports': []}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_valores(self, erros: list) -> None:
        cfop = self._texto(self.Cd_CFOP)
        if (cfop in ['2101','2102','2551','2556','2406','2407']) and abs(self._valor("VL_DIFAL")) <= 1:
            self._erro(erros, "VL_DIFAL", f"Verificar VL_DIFAL — não parece correto; CFOP = {cfop}")
        if abs(self._valor("VL_TOT_LIQ")) <= 1:
            self._erro(erros, "VL_TOT_LIQ", "Verificar VL_TOT_LIQ — não parece correto")
```

</details>

---

<a id="funcao-342"></a>

## _validar_aliquotas

Valida as alíquotas de IPI e ICMS em relação aos valores totais.

Verifica se as alíquotas de IPI e ICMS estão corretamente relacionadas aos valores totais de IPI, ICMS e líquido. Se não estiverem, adiciona um erro à lista de erros fornecida.

### Assinatura

```python
def _validar_aliquotas(self, erros: list) -> None:
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém os métodos e atributos. |
| `erros` | `list` | Lista onde serão adicionados quaisquer erros encontrados durante a validação. |

### Retorno

**Tipo:** `None`

Não retorna nenhum valor. Modifica a lista de erros diretamente.

### Dependências

- `{'nome': 'abs', 'categoria': 'chamada', 'descricao': 'Função utilizada para calcular o valor absoluto.'}`
- `{'nome': 'self._erro', 'categoria': 'chamada', 'descricao': 'Método da instância que adiciona um erro à lista de erros.'}`
- `{'nome': 'self._valor', 'categoria': 'chamada', 'descricao': 'Método da instância que retorna o valor associado a uma chave específica.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def _validar_aliquotas(self, erros: list) -> None:
        vl_ipi = self._valor("VL_TOT_IPI")
        vl_icms = self._valor("VL_TOT_ICMS")
        vl_liq = self._valor("VL_TOT_LIQ")
        total = vl_ipi + vl_icms + vl_liq
        if total <= 0:
            return
        if abs(vl_ipi / total - self._valor("ALIQ_IPI")) > 1e-6:
            self._erro(erros, "ALIQ_IPI", "Verificar ALIQ_IPI ou VL_TOT_IPI — não parecem corretos")
        if abs(vl_icms / total - self._valor("ALIQ_ICMS")) > 1e-3:
            self._erro(erros, "ALIQ_ICMS", "Verificar ALIQ_ICMS ou VL_TOT_ICMS — não parecem corretos")
```

</details>

---

<a id="funcao-343"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-344"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len = 1000)
```

</details>

---

<a id="funcao-345"></a>

## validar_txt1

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máxima.

### Assinatura

```python
def validar_txt1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)
```

</details>

---

<a id="funcao-346"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-347"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-348"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 99, inclusive. Utiliza uma validação interna para garantir este critério.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
         return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-349"></a>

## validar_TUC

Valida um valor como código de Unidade Curricular (UC).

Verifica se o valor fornecido é válido como código de UC, considerando que deve ser um número inteiro entre 100 e 999, conforme definido em ValoresTUC.teste(). Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado como inteiro.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-350"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-351"></a>

## validar_ITEM

Valida um item de texto com uma restrição de comprimento máximo.

A função valida se o valor fornecido é um texto e, opcionalmente, verifica se seu comprimento não excede 25 caracteres. Utiliza a validação interna do Pydantic para garantir que o valor seja um texto válido.

### Assinatura

```python
def validar_ITEM(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente no código chamador). |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, que deve ser um texto.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ITEM(cls, v, info):
        return validar_texto(v, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-352"></a>

## validar_ITEM1

Valida um valor de acordo com regras específicas.

A função valida um valor utilizando uma validação personalizada definida em `validar_texto`. Permite que o valor esteja vazio e tem um limite máximo de caracteres de 25.

### Assinatura

```python
def validar_ITEM1(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ITEM1(cls, v, info):
        return validar_texto(v, info.field_name, vazio=True, max_len=25)
```

</details>

---

<a id="funcao-353"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'field_validator', 'categoria': 'chamada'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-354"></a>

## validar_NRform

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, especificamente um número de registro (NRform), utilizando uma validação textual. Ela chama a função `validar_texto`, passando o valor, o nome do campo e um comprimento máximo de 7 caracteres.

### Assinatura

```python
def validar_NRform(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=7)
```

</details>

---

<a id="funcao-355"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-356"></a>

## validar_TUC

Valida um valor conforme regras específicas do domínio TUC.

A função valida se o valor está dentro de um intervalo específico (0 a 100) e se atende aos critérios definidos pela classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

Valor após a validação, se for válido.

### Exceções

- **`ValueError`**: Quando o valor não é válido no domínio ou não atende aos critérios definidos pela classe ValoresTUC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=0, max_val=100)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido no domínio ({value}).\n')
        return nm
```

</details>

---

<a id="funcao-357"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-358"></a>

## validar_ITEM

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

Esta função é usada para validar um valor como decimal, utilizando uma validação personalizada definida em outro lugar. Ela garante que o valor seja maior ou igual a zero.

### Assinatura

```python
def validar_ITEM(cls, v):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em contextos de validação de modelos Pydantic). |
| `v` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Se não for válido, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ITEM(cls, v):
        return validar_decimal(v, min_val=0)
```

</details>

---

<a id="funcao-359"></a>

## validar_FLG

Valida se um valor é uma flag booleana (0 ou 1).

A função valida que o valor fornecido está entre 0 e 1, inclusos. Utiliza a validação de inteiro para garantir que o valor esteja dentro do intervalo especificado.

### Assinatura

```python
def validar_FLG(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a função é definida. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-360"></a>

## validar_Dt

Valida uma data, permitindo que o valor seja vazio.

Esta função utiliza um validador de campo para verificar se a data fornecida é válida. Ela aceita tanto datas como valores vazios, conforme especificado pelo parâmetro `vazio=True` no chamada à função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma data. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-361"></a>

## validar_Dtr

Valida um valor utilizando uma função de validação específica.

Esta função utiliza um validador de campo para verificar a validade do valor fornecido. O parâmetro `vazio=True` permite que o valor seja vazio, caso contrário, seria considerado inválido.

### Assinatura

```python
def validar_Dtr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a validação está sendo aplicada. |
| `value` | `Não especificado` | Valor que será validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dtr(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-362"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida que o valor fornecido seja um número inteiro dentro do intervalo de 0 a 99. Também permite que o valor esteja vazio, conforme especificado pelo parâmetro `vazio`.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
```

</details>

---

<a id="funcao-363"></a>

## validar_TUC

Valida um valor como código de Unidade Curricular (UC).

Verifica se o valor fornecido é válido como código de UC, considerando que deve ser um número inteiro entre 100 e 999, conforme definido em ValoresTUC.teste(). Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado como inteiro.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-364"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-365"></a>

## validar_ide1

Valida um valor como inteiro, permitindo valores vazios.

A função valida se o valor fornecido é um inteiro e permite que seja vazio. Utiliza uma validação interna para verificar a condição de integridade do valor.

### Assinatura

```python
def validar_ide1(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em métodos de classe). |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1, vazio=True)
```

</details>

---

<a id="funcao-366"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele está vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
```

</details>

---

<a id="funcao-367"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo é válido, considerando um comprimento máximo e permitindo valores vazios.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o validador. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
```

</details>

---

<a id="funcao-368"></a>

## validar_cdop

Valida um valor conforme regras específicas para CDOP.

A função valida um valor utilizando uma validação de texto, permitindo valores vazios e limitando a sua extensão máxima em 50 caracteres.

### Assinatura

```python
def validar_cdop(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cdop(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
```

</details>

---

<a id="funcao-369"></a>

## validar_NRform

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo.

### Assinatura

```python
def validar_NRform(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação, ou lança uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-370"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que o método é definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-371"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-372"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele está vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 1000, vazio=True)
```

</details>

---

<a id="funcao-373"></a>

## validar_txt1

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máxima.

### Assinatura

```python
def validar_txt1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)
```

</details>

---

<a id="funcao-374"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que o método é definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-375"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-376"></a>

## validar_al

Valida um valor como decimal dentro de um intervalo específico.

A função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se ele está dentro do intervalo definido por min_val e max_val. Se o valor for inválido, uma exceção será lançada.

### Assinatura

```python
def validar_al(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_al(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-377"></a>

## validar_vl_cdng

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido esteja entre 4 e 7, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=4, max_val=7)
```

</details>

---

<a id="funcao-378"></a>

## validar_und

Valida um valor de acordo com regras específicas para uma unidade.

A função valida o valor fornecido utilizando a função `validar_texto`, limitando-o a uma máxima extensão de 10 caracteres. O nome do campo é passado para fins de contexto na validação.

### Assinatura

```python
def validar_und(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_und(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-379"></a>

## validar_cnpj

Valida um CNPJ utilizando uma função auxiliar.

Esta função utiliza um validador de CNPJ para verificar a validade do valor fornecido. A verificação é realizada por meio de uma chamada à função `validar_CNPJ`.

### Assinatura

```python
def validar_cnpj(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como CNPJ. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_CNPJ`, que indica se o CNPJ é válido ou não.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cnpj(cls, value):
        return validar_CNPJ(value)
```

</details>

---

<a id="funcao-380"></a>

## validar_serie

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido está entre 1 e 1000000, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro válido.

### Assinatura

```python
def validar_serie(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_serie(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=1000000)
```

</details>

---

<a id="funcao-381"></a>

## validar_nr

Valida se um valor é um número inteiro.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número inteiro. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_nr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr(cls, value, info):
        return validar_inteiro(value, info.field_name)
```

</details>

---

<a id="funcao-382"></a>

## validar_NFe

Valida um valor como inteiro, permitindo valores vazios.

A função valida se o valor fornecido é um número inteiro. Ela aceita valores vazios conforme especificado pelo parâmetro `vazio=True` no chamado à função `validar_inteiro`.

### Assinatura

```python
def validar_NFe(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como inteiro. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NFe(cls, value, info):
        return validar_inteiro(value, info.field_name, vazio=True)
```

</details>

---

<a id="funcao-383"></a>

## validar_FLG

Valida se um valor é uma flag booleana (0 ou 1).

A função valida que o valor fornecido está entre 0 e 1, inclusos. Utiliza a validação de inteiro para garantir que o valor esteja dentro do intervalo especificado.

### Assinatura

```python
def validar_FLG(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe onde a função é definida. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-384"></a>

## validar_TPFAT

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 10, inclusos. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_TPFAT(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TPFAT(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1, max_val=10)
```

</details>

---

<a id="funcao-385"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo atende aos critérios especificados, incluindo uma máxima comprimento de 25 caracteres e permitindo valores vazios.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-386"></a>

## validar_cd1

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 150 caracteres.

### Assinatura

```python
def validar_cd1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, conforme retornado pela função `validar_texto`.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=150)
```

</details>

---

<a id="funcao-387"></a>

## verifica_dados

Verifica os dados fornecidos e manipula erros de validação.

Esta função verifica se os dados fornecidos são válidos através de um handler. Se ocorrer uma exceção de validação, a função tenta construir o modelo novamente com os valores fornecidos. Em seguida, verifica condições específicas relacionadas aos atributos 'Cd_NG', 'Desc_SERV' e 'COD_ITEM'. Caso as condições não sejam atendidas, levanta um erro ValueError com uma mensagem específica.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem verificados e manipulados. |
| `handler` | `Não especificado` | Função que realiza a validação dos dados. |

### Retorno

**Tipo:** `Não especificado`

O resultado do handler ou o modelo construído em caso de erro de validação.

### Exceções

- **`ValueError`**: Quando a descrição do serviço não é declarada para 'Cd_NG' diferente de '4', ou quando o COD_ITEM não é declarado para 'Cd_NG' igual a '4'.
- **`ValidationError`**: Quando ocorre uma exceção de validação durante a execução do handler.

### Dependências

- `{'nome': 'pydantic.model_validator', 'categoria': 'import'}`
- `{'nome': 'ValueError', 'categoria': 'chamada'}`
- `{'nome': 'cls.model_construct', 'categoria': 'chamada'}`
- `{'nome': 'getattr', 'categoria': 'chamada'}`
- `{'nome': 'handler', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_Ext_SRV", "—")
        Cd_NG = getattr(result, "Cd_NG", None)
        Desc_SERV = getattr(result, "Desc_SERV", None)
        COD_ITEM = getattr(result, "COD_ITEM", None)

        if (Cd_NG != "4") and (Desc_SERV in ["", None]):
            raise ValueError(f"Deve ser declarada a descrição do serviço, linha {linha}.\n")
        if (Cd_NG == "4") and (COD_ITEM in ["", None]):
            raise ValueError(f"Deve ser declarada COD_ITEM do serviço, linha {linha}.\n")
        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-388"></a>

## validar_ide

Valida um valor utilizando uma função de validação específica.

Esta função é usada como um decorador para validar um campo em um modelo Pydantic. Ela chama a função `validar_data` para realizar a validação do valor fornecido.

### Assinatura

```python
def validar_ide(cls, v):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o campo sendo validado. |
| `v` | `Não especificado` | Valor a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v):
        return validar_data(v)
```

</details>

---

<a id="funcao-389"></a>

## validar_ide1

Valida se um valor é um inteiro e maior ou igual a 1.

Esta função valida que o valor fornecido seja um número inteiro e que ele seja maior ou igual a 1. Utiliza uma validação personalizada definida em outra função chamada `validar_inteiro`.

### Assinatura

```python
def validar_ide1(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val = 1)
```

</details>

---

<a id="funcao-390"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 1000)
```

</details>

---

<a id="funcao-391"></a>

## validar_txt1

Valida um valor de texto com base em regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máxima. Utiliza uma validação personalizada definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt1(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 10)
```

</details>

---

<a id="funcao-392"></a>

## validar_cd

Valida um valor de CD (Código de Dados) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a 50 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len = 50)
```

</details>

---

<a id="funcao-393"></a>

## validar_ide2

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação personalizada definida em outra parte do código, provavelmente dentro de uma classe Pydantic.

### Assinatura

```python
def validar_ide2(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide2(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val = 0)
```

</details>

---

<a id="funcao-394"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que o método é definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-395"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 99, inclusive. Utiliza uma validação interna para garantir este critério.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-396"></a>

## validar_TUC

Valida um valor como código de Unidade Curricular (UC).

Verifica se o valor fornecido é válido como código de UC, considerando que deve ser um número inteiro entre 100 e 999, conforme definido em ValoresTUC.teste(). Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado como inteiro.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=100, max_val=999, vazio=True)
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return nm
```

</details>

---

<a id="funcao-397"></a>

## validar_UAR

Valida se o valor pertence a um conjunto específico de domínios.

A função valida que o valor fornecido é uma string e pertence ao domínio ['UC', 'UAR', 'TUC']. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_UAR(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, dominio=['UC','UAR','TUC'])
```

</details>

---

<a id="funcao-398"></a>

## validar_ide1

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide1(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-399"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-400"></a>

## validar_cds

Valida um valor de campo em um modelo Pydantic.

Aplica uma validação de texto a um valor específico, limitando sua comprimento máximo a 50 caracteres. Utiliza um validador de campo do Pydantic para realizar a verificação.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
```

</details>

---

<a id="funcao-401"></a>

## validar_cds1

Valida um valor de acordo com regras específicas para texto.

A função valida o valor fornecido, verificando se ele é um texto válido e opcionalmente limitando sua comprimento. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_cds1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50, vazio=True)
```

</details>

---

<a id="funcao-402"></a>

## validar_dig_inc

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_dig_inc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-403"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-404"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor válido após a validação.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        nm = validar_inteiro(value, info.field_name, min_val=1, max_val=100, vazio=True)
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return nm
```

</details>

---

<a id="funcao-405"></a>

## validar_TUC

Valida se um valor é válido como código de UC (Unidade Curricular).

Verifica se o valor fornecido atende aos critérios definidos pela classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, geralmente fornecido pelo Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
```

</details>

---

<a id="funcao-406"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 99, inclusive. Utiliza uma validação interna para garantir este critério.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-407"></a>

## validar_ide

Valida um valor de acordo com regras específicas para campos de texto.

A função valida o valor fornecido, considerando se está vazio e limitando seu comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=50)
```

</details>

---

<a id="funcao-408"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'field_validator', 'categoria': 'chamada'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-409"></a>

## validar_NRform

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo.

### Assinatura

```python
def validar_NRform(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação, ou lança uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-410"></a>

## validar_vl

Valida um valor decimal, garantindo que ele seja maior ou igual a zero.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se ele atende ao critério de ser maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser um número decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val = 0)
```

</details>

---

<a id="funcao-411"></a>

## verifica_dados

Verifica os dados utilizando um manipulador e validações específicas.

A função verifica os dados fornecidos usando um manipulador, capturando quaisquer erros de validação. Se ocorrerem erros, tenta construir o modelo novamente com os valores fornecidos. Em seguida, realiza validações adicionais e pode lançar exceções se as validações falharem.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem verificados e validados. |
| `handler` | `Não especificado` | Função ou método que processa os valores e pode lançar uma exceção de validação. |

### Retorno

**Tipo:** `Não especificado`

O resultado do manipulador após as verificações.

### Exceções

- **`ValueError`**: Quando ocorrer um erro de validação durante a verificação adicional.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_BX_INC", "—")
        Nr_CM = getattr(result, "Nr_CM", None)
        Nr_TI = getattr(result, "Nr_TI", None)

        try:
            validar_cm(Nr_TI, Nr_CM, linha)
            validar_ti_distribuicao(Nr_TI, linha)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-412"></a>

## validar_cds

Valida um valor de acordo com as regras definidas em `validar_texto`.

Esta função é usada para validar um valor, verificando se ele atende aos critérios estabelecidos pela função `validar_texto`, limitando a sua comprimento máximo em 50 caracteres.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
```

</details>

---

<a id="funcao-413"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-414"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-415"></a>

## validar_cd

Valida um valor de campo em uma classe usando a função `validar_texto`.

Esta função é usada como um validador de campo em classes Pydantic. Ela chama a função `validar_texto` para verificar se o valor do campo atende aos critérios especificados, incluindo uma máxima comprimento de 25 caracteres e permitindo valores vazios.

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-416"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-417"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-418"></a>

## validar_ide3

Valida se um valor é um inteiro e maior ou igual a 1.

A função utiliza um validador de campo para verificar se o valor fornecido é um inteiro e se ele é maior ou igual a 1. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide3(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide3(cls, value, info):
         return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-419"></a>

## validar_ide2

Valida um valor de acordo com regras específicas para texto.

A função valida o valor fornecido, verificando se ele é um texto e limitando sua comprimento máximo a 5 caracteres. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_ide2(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide2(cls, v, info):
        return validar_texto(v, info.field_name, max_len=5)
```

</details>

---

<a id="funcao-420"></a>

## validar_ide

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-421"></a>

## validar_ide1

Valida um valor de texto com base em regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_ide1(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, v, info):
        return validar_texto(v, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-422"></a>

## validar_ideais

Valida se um valor é um inteiro ideal.

Verifica se o valor fornecido é um inteiro e, caso contrário, lança uma exceção. O valor mínimo aceitável é 1.

### Assinatura

```python
def validar_ideais(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ideais(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-423"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

Verifica se o valor fornecido é válido conforme a regra definida em ValoresTI.teste. Lança uma exceção ValueError caso o valor não seja válido.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        if (value is not None) and (not ValoresTI.teste(int(value))):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
```

</details>

---

<a id="funcao-424"></a>

## validar_TUC

Valida se um valor é válido como código de UC (Unidade Curricular).

Verifica se o valor fornecido é um código de UC válido utilizando a função `ValoresTUC.teste`. Se o valor for inválido, lança uma exceção `ValueError`.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código de UC. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, geralmente fornecidas pelo Pydantic. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        if (value is not None) and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
```

</details>

---

<a id="funcao-425"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99, permitindo valores vazios.

A função valida que o valor fornecido seja um número inteiro dentro do intervalo de 0 a 99. Também permite que o valor esteja vazio, conforme especificado pelo parâmetro `vazio`.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        validar_inteiro(value, info.field_name, min_val=0, max_val=99, vazio=True)
```

</details>

---

<a id="funcao-426"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-427"></a>

## validar_cds

Valida um valor de acordo com regras específicas para CDS (Common Data Standard).

A função utiliza um validador de texto personalizado para verificar se o valor fornecido atende aos critérios de comprimento máximo definidos.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-428"></a>

## validar_cds1

Valida um valor de acordo com regras específicas para texto.

A função valida o valor fornecido, verificando se ele é um texto e limitando sua comprimento máximo. Também permite que o valor esteja vazio.

### Assinatura

```python
def validar_cds1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000, vazio=True)
```

</details>

---

<a id="funcao-429"></a>

## validar_dig_inc

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_dig_inc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-430"></a>

## validar_CC

Valida se um valor pertence ao domínio definido por ValoresCC.

Verifica se o valor fornecido é válido de acordo com as regras estabelecidas em ValoresCC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_CC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não pertence ao domínio definido por ValoresCC.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value):
        if not ValoresCC.teste(value):
            raise ValueError(f'{value} dado não faz parte do domínio.\n')
        return value
```

</details>

---

<a id="funcao-431"></a>

## validar_UAR

Valida se o valor é uma UAR (Unidade Administrativa Regional) conforme regras específicas.

A função valida que o valor fornecido seja uma das opções permitidas ('UC', 'UAR', 'TUC') e que não ultrapasse a quantidade máxima de caracteres especificada (3). Utiliza um validador de campo para realizar a verificação.

### Assinatura

```python
def validar_UAR(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo sendo validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['UC','UAR','TUC'])
```

</details>

---

<a id="funcao-432"></a>

## validar_NRform

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo.

### Assinatura

```python
def validar_NRform(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original após a validação, ou lança uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NRform(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-433"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

Esta função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value, info):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-434"></a>

## verifica_dados

Verifica os dados fornecidos utilizando um manipulador e regras de validação específicas.

A função verifica se os dados fornecidos são válidos através de um manipulador. Se ocorrerem erros de validação, tenta construir um modelo a partir dos valores fornecidos. Em seguida, realiza várias verificações adicionais e pode lançar exceções se qualquer uma das verificações falhar.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `values` | `Não especificado` | Valores a serem verificados. |
| `handler` | `Não especificado` | Função que manipula os valores e pode lançar exceções de validação. |

### Retorno

**Tipo:** `Não especificado`

O resultado da verificação, que pode ser um modelo construído ou outro objeto dependendo do sucesso das verificações.

### Exceções

- **`ValueError`**: Quando ocorrerem erros de validação durante as verificações adicionais.

### Dependências

- `pandas`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_SEQ_PP", "—")
        Nr_CM = getattr(result, "Nr_CM", None)
        Nr_TI = getattr(result, "Nr_TI", None)
        Dt_REF = getattr(result, "Dt_REF_DADOS", None)
        dt_INI = (
                    pd.to_datetime(st.session_state.dt_ini)
                    - pd.Timedelta(days=1)
                ).strftime("%Y/%m/%d")

        try:
            val_dt(Dt_REF, dt_INI)
            validar_cm(Nr_TI, Nr_CM, linha)
            validar_ti_distribuicao(Nr_TI, linha)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-435"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-436"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-437"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-438"></a>

## validar_ide1

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-439"></a>

## validar_ideais

Valida um valor como um inteiro ideal.

Verifica se o valor é um número inteiro, aceitando valores vazios e limitando-os a partir de 1.

### Assinatura

```python
def validar_ideais(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ideais(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, vazio=True)
```

</details>

---

<a id="funcao-440"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_decimal', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0)
```

</details>

---

<a id="funcao-441"></a>

## validar_vl_pct_ori

Valida se um valor é uma porcentagem decimal válida.

Verifica se o valor fornecido está dentro do intervalo de 0 a 1, inclusivo. Utiliza uma validação decimal personalizada para garantir que o valor seja válido como uma porcentagem.

### Assinatura

```python
def validar_vl_pct_ori(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente no código) |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_pct_ori(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0, max_val = 1)
```

</details>

---

<a id="funcao-442"></a>

## validar_ide2

Valida um valor como inteiro dentro de um intervalo específico.

A função valida se o valor fornecido é um inteiro e se está dentro do intervalo definido por min_val e max_val. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide2(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-443"></a>

## verifica_dados

Verifica os dados utilizando um manipulador e valida a data de referência.

A função verifica se os dados fornecidos são válidos através de um manipulador. Se ocorrer uma validação de erro, o objeto é construído novamente usando `model_construct`. A função também valida a data de referência em relação à data final e levanta um erro se a validação falhar.

### Assinatura

```python
def verifica_dados(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, usada para construir o objeto. |
| `values` | `Não especificado` | Valores a serem verificados e manipulados. |
| `handler` | `Não especificado` | Função que realiza a validação dos dados. |

### Retorno

**Tipo:** `Não especificado`

Objeto resultante após a verificação e manipulação.

### Exceções

- **`ValueError`**: Quando ocorre um erro de validação ou uma data inválida.

### Dependências

- `pandas`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def verifica_dados(cls, values, handler):
        validation_error = None
        try:
            result = handler(values)
        except ValidationError as e:
            validation_error = e
            result = cls.model_construct(**values)

        linha = getattr(result, "Id_SEQ_PP", "—")
        Dt_REF = getattr(result, "Dt_REF_DADOS", None)
        dt_FIM = (
                    pd.to_datetime(st.session_state.dt_fim)
                    - pd.Timedelta(days=0)
                ).strftime("%Y/%m/%d")

        try:
            val_dt(Dt_REF, dt_FIM)
        except ValueError as ex:
            raise ValueError(f"Erro: {ex}") from ex

        if validation_error is not None:
            raise validation_error

        return result
```

</details>

---

<a id="funcao-444"></a>

## validar_ide2a

Valida um texto conforme regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo.

### Assinatura

```python
def validar_ide2a(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide2a(cls, v, info):
        return validar_texto(v, info.field_name, max_len=5)
```

</details>

---

<a id="funcao-445"></a>

## validar_vl_pct_ori

Valida se um valor é uma porcentagem decimal válida.

Verifica se o valor fornecido está dentro do intervalo de 0 a 1, inclusivo. Utiliza uma validação decimal personalizada para garantir que o valor seja um número válido e esteja no intervalo especificado.

### Assinatura

```python
def validar_vl_pct_ori(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente não utilizado diretamente nesta função). |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Caso contrário, uma exceção será levantada.

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_decimal']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_pct_ori(cls, value, info):
        return validar_decimal(value, info.field_name, min_val = 0, max_val = 1)
```

</details>

---

<a id="funcao-446"></a>

## validar_ide

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-447"></a>

## validar_cd

Valida um valor de CD utilizando uma função de texto.

Esta função valida um valor de CD chamando outra função `validar_texto`, verificando se o valor não excede a largura máxima permitida (25 caracteres).

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-448"></a>

## validar_cdx

Valida um valor de acordo com regras específicas para campos de texto.

A função valida o valor fornecido, considerando se está vazio e limitando sua comprimento máximo. Utiliza uma validação interna chamada 'validar_texto'.

### Assinatura

```python
def validar_cdx(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cdx(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
```

</details>

---

<a id="funcao-449"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-450"></a>

## validar_Dt1

Valida uma data, permitindo que ela seja vazia.

Esta função valida se um valor é uma data válida, considerando a opção de ser vazia. Utiliza outra função chamada 'validar_data' para realizar o processo de validação.

### Assinatura

```python
def validar_Dt1(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor a ser validado como data. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt1(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-451"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-452"></a>

## validar_ide1

Valida se um valor é um inteiro e maior ou igual a 1.

A função valida que o valor fornecido é um número inteiro e verifica se ele é maior ou igual a 1. Utiliza uma validação personalizada definida em outra parte do código, provavelmente dentro de uma classe Pydantic.

### Assinatura

```python
def validar_ide1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-453"></a>

## validar_ide2

Valida um valor inteiro dentro de um intervalo específico.

A função valida se o valor fornecido está entre 1 e 4, inclusos. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide2(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide2(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1,max_val=4)
```

</details>

---

<a id="funcao-454"></a>

## validar_ide3

Valida um valor inteiro dentro de um intervalo específico.

A função valida se o valor fornecido está entre 1 e 5, inclusos. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide3(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide3(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1,max_val=5)
```

</details>

---

<a id="funcao-455"></a>

## validar_ideais

Valida um valor como um inteiro ideal.

Verifica se o valor é um número inteiro, permitindo valores vazios e especificando um valor mínimo.

### Assinatura

```python
def validar_ideais(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ideais(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=0, vazio=True)
```

</details>

---

<a id="funcao-456"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido é um número inteiro e, em seguida, verifica se ele atende aos critérios específicos para ser considerado um TI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como TI. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido como TI, caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o dado não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        numero = validar_inteiro(value, info.field_name)
        if not ValoresTI.teste(int(numero)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
```

</details>

---

<a id="funcao-457"></a>

## validar_TUC

Valida se um valor é válido como código de UC (Unidade Curricular).

A função valida se o valor fornecido é um número inteiro e, em seguida, verifica se ele atende aos critérios definidos pela classe ValoresTUC. Se não for válido, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como código de UC.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        numero = validar_inteiro(value, info.field_name)
        if not ValoresTUC.teste(int(numero)):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
```

</details>

---

<a id="funcao-458"></a>

## validar_nr_a1

Valida se um valor é um número inteiro entre 0 e 99.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 99, inclusive. Utiliza uma validação interna para garantir este critério.

### Assinatura

```python
def validar_nr_a1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_nr_a1(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-459"></a>

## validar_txt

Valida um valor de texto conforme regras específicas.

A função valida um valor de texto, permitindo que esteja vazio e limitando sua comprimento máximo a 1000 caracteres. Utiliza uma validação interna definida em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`
- `{'nome': 'field_validator', 'categoria': 'chamada'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-460"></a>

## validar_sisbase

Valida um valor conforme as regras definidas para o campo SISBASE.

A função valida se o valor fornecido é uma string de texto com no máximo 6 caracteres, permitindo valores vazios.

### Assinatura

```python
def validar_sisbase(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção de validação.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_sisbase(cls, value, info):
        return validar_texto(value, info.field_name, max_len=6, vazio=True)
```

</details>

---

<a id="funcao-461"></a>

## validar_cds

Valida um valor de acordo com regras específicas para CDS.

A função valida um valor utilizando uma validação de texto, permitindo valores vazios e limitando a sua comprimento máximo em 25 caracteres. Esta função é usada como um decorador de validação em classes Pydantic.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-462"></a>

## validar_dig_inc

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_dig_inc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-463"></a>

## validar_CC

Valida um valor contra um conjunto de regras definidas em ValoresCC.

Verifica se o valor fornecido está dentro do domínio aceito conforme definido pela classe ValoresCC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_CC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a lógica de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação.

### Exceções

- **`ValueError`**: Quando o valor não está dentro do domínio aceito.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value):
        if not ValoresCC.teste(value):
            raise ValueError(f'{value} fora do domínio aceito.\n')
        return value
```

</details>

---

<a id="funcao-464"></a>

## validar_UAR

Valida se o valor pertence a um conjunto específico de domínios.

A função valida que o valor fornecido é uma string e pertence ao domínio ['UC', 'TUC', 'UAR']. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_UAR(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, dominio = ['UC','TUC','UAR'])
```

</details>

---

<a id="funcao-465"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a uma máxima extensão de 10 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-466"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que o método é definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-467"></a>

## validar_regras_de_dominio

Valida regras de domínio para dados específicos.

Esta função valida um conjunto de regras de domínio para dados fornecidos, utilizando um manipulador personalizado. Ela verifica várias condições e gera erros se as regras não forem atendidas.

### Assinatura

```python
def validar_regras_de_dominio(cls, values, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, usada para construir um modelo de dados. |
| `values` | `Não especificado` | Dados a serem validados. |
| `handler` | `Não especificado` | Manipulador personalizado para processar os dados. |

### Retorno

**Tipo:** `Não especificado`

Resultado da validação dos dados, ou lança uma exceção se as regras não forem atendidas.

### Exceções

- **`ValidationError`**: Quando ocorrem erros de validação durante a execução do manipulador.

### Dependências

- `pydantic.ValidationError`
- `re`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_regras_de_dominio(cls, values, handler):
        erros = []
        invalidos = set()
        try:
            resultado = handler(values)
        except ValidationError as exc:
            erros.extend(exc.errors(include_url=False))
            invalidos = {e["loc"][0] for e in erros if e.get("loc")}
            if not isinstance(values, dict):
                raise
            resultado = cls.model_construct(**values)

        def texto(campo):
            valor = getattr(resultado, campo, None)
            return "" if valor is None else str(valor).strip()

        def validar_tp_bem(ti, tuc, cc, tp_bem, linha):
            try:
                ti_num = int(ti)
            except (ValueError, TypeError):
                ti_num = None
            try:
                tuc_num = int(tuc)
            except (ValueError, TypeError):
                tuc_num = None

            tp_bem = str(tp_bem).strip()
            cc = str(cc).strip()

            motivos = []

            if ti_num is not None and (
                                            70 <= ti_num <= 91
                                            or ti_num in {94, 95, 97, 99}
                                        ):
                motivos.append(f"Nr_TI={ti}")

            if tuc_num in {230, 235, 535}:
                motivos.append(f"Nr_TUC={tuc}")

            if re.fullmatch(r"1232\d0\d05", cc):
                motivos.append(f"Cd_CC={cc} (veículos)")

            if motivos and tp_bem != "4":
                raise ValueError(
                    f"Id_SEQ_INC={linha}: TP_BEM esperava-se ser 4 "
                    f"quando houver enquadramento em "
                    f"{', '.join(motivos)}. "
                    f"Valor informado: TP_BEM={tp_bem}."
                )
        def validar_voc_ca_avaliacao_2(tp_aval, voc_ca, com_voc, linha):
            if str(tp_aval).strip() != "2":
                return
            try:
                valor_ca = float(voc_ca)
            except (TypeError, ValueError):
                return

            if float(valor_ca) == 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Para Cd_TP_AVAL=2, "
                    "VL_VOC_CA não pode ser zero. "
                    f"VL_COM_VOC={com_voc}; VL_VOC_CA={voc_ca}."
                )

        def validar_pct_oe(flg_doa, flg_incor, flg_plpt, pct_oe, linha):

            flags = {
                        "FLG_DOA_OE": flg_doa,
                        "FLG_INCOR_OE": flg_incor,
                        "FLG_PLPT_OE": flg_plpt
                    }

            flags_ativas = [
                                campo
                                for campo, valor in flags.items()
                                if str(valor).strip() == "1"
                            ]

            if (not flags_ativas):
                return

            try:
                percentual = float(str(pct_oe).strip().replace(",", "."))
            except (ValueError, TypeError):
                return
            
            if not percentual > 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Pct_OE deve ser maior que zero "
                    f"quando pelo menos um dos indicadores "
                    f"{', '.join(flags_ativas)} for igual a 1. "
                    f"Valor informado: Pct_OE={pct_oe}."
                )

        def executar(campo, dependencias, funcao, *args):
            if any(dep in invalidos for dep in dependencias):
                return
            try:
                funcao(*args)
            except (ValueError, TypeError, ArithmeticError) as exc:
                mensagem = str(exc).strip()
                erros.append({
                                "type": "value_error",
                                "loc": (campo,),
                                "input": getattr(resultado, campo, None),
                                "ctx": {"error": ValueError(mensagem)},
                            })

        linha = texto("Id_SEQ_INC")
        ti, cm, cc = texto("Nr_TI"), texto("Nr_CM"), texto("Cd_CC")
        tuc, a1 = texto("Nr_TUC"), texto("Nr_A1")
        a3, a4, a5 = texto("Nr_A3"), texto("Nr_A4"), texto("Nr_A5")
        und = texto("Cd_UND_AIS")
        tp_aval = texto("Cd_TP_AVAL")
        voc_ca = texto("VL_VOC_CA")
        com_voc = texto("VL_COM_VOC")
        tp_bem = texto("TP_BEM")
        flg_doa = texto("FLG_DOA_OE")
        flg_incor = texto("FLG_INCOR_OE")
        flg_plpt = texto("FLG_PLPT_OE")
        pct_oe = texto("Pct_OE")

        executar("Nr_CM", ("Nr_TI", "Nr_CM"), validar_cm, ti, cm, linha)
        executar("Nr_TI", ("Nr_TI",), validar_ti_distribuicao, ti, linha)
        executar("Cd_CC", ("Nr_TI", "Cd_CC"), validar_administracao, ti, cc, linha)
        executar("Nr_TUC", ("Nr_TUC", "Nr_A1", "Nr_A3", "Nr_A4", "Nr_A5", "Cd_UND_AIS"),
                 validar_cabos, tuc, a1, a3, a4, a5, und, linha)
        executar("Nr_TUC", ("Nr_TI", "Nr_TUC", "Nr_A1"),
                 validar_torre_poste, ti, tuc, a1, linha)
        executar("Nr_TUC", ("Nr_TUC",), validar_tucs_proibidos, tuc, linha)
        executar("VL_VOC_CA", ("Cd_TP_AVAL", "VL_VOC_CA", "VL_COM_VOC"), validar_voc_ca_avaliacao_2,
                 tp_aval, voc_ca, com_voc, linha)
        executar("TP_BEM", ("TP_BEM",), validar_tp_bem, ti, tuc,
                    cc, tp_bem, linha)
        executar("Pct_OE", ("Pct_OE", "FLG_DOA_OE", "FLG_INCOR_OE", "FLG_PLPT_OE"), validar_pct_oe, 
                 flg_doa, flg_incor, flg_plpt, pct_oe, linha)

        if erros:
            raise ValidationError.from_exception_data(cls.__name__, erros)
        return resultado
```

</details>

---

<a id="funcao-468"></a>

## validar_cd

Valida um valor de CD utilizando uma função de texto.

Esta função valida um valor de CD chamando outra função `validar_texto`, verificando se o valor não excede a largura máxima permitida (25 caracteres).

### Assinatura

```python
def validar_cd(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-469"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-470"></a>

## validar_FLG

Valida se um valor é uma inteiro entre 0 e 1.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 1, inclusivo. Utiliza um validador de campo para realizar essa verificação.

### Assinatura

```python
def validar_FLG(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_inteiro', 'tipo': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_FLG(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-471"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-472"></a>

## validar_txt

Valida um valor de texto em um contexto específico.

A função valida um valor de texto, verificando se ele atende a certos critérios, incluindo o comprimento máximo. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def validar_txt(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, como seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_txt(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-473"></a>

## validar_CC

Valida um número de cartão de crédito (CC) utilizando uma função auxiliar.

A função valida o valor fornecido como um número de cartão de crédito, verificando se ele atende a determinados critérios definidos em outra função chamada `validar_texto`. O parâmetro `info.field_name` é usado para obter o nome do campo que está sendo validado.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usada em métodos de classe). |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente um número de cartão de crédito. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_texto`, que é responsável por realizar a validação específica do número de cartão de crédito.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=9)
```

</details>

---

<a id="funcao-474"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a uma máxima extensão de 10 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-475"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-476"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-477"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-478"></a>

## validar_CC

Valida um número de cartão de crédito (CC).

Verifica se o valor fornecido é uma string que representa um número de cartão de crédito válido, com no máximo 15 caracteres.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma string. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
```

</details>

---

<a id="funcao-479"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a 15 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
```

</details>

---

<a id="funcao-480"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-481"></a>

## validar_TUC

Valida se um valor pertence ao domínio definido pela classe ValoresTUC.

Verifica se o valor fornecido é válido de acordo com a regra definida na classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a lógica de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não pertence ao domínio definido pela classe ValoresTUC.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'{value} não pertence ao domínio da variável.\n')
        return value
```

</details>

---

<a id="funcao-482"></a>

## validar_CC

Valida um valor de cartão de crédito (CC) utilizando uma função de validação de texto.

A função valida o valor do cartão de crédito, verificando se ele atende aos critérios definidos em 'validar_texto'. O parâmetro 'max_len' é fixado em 25, limitando a quantidade máxima de caracteres permitidos no valor do CC.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do cartão de crédito a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função 'validar_texto'.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Método de validação do Pydantic.'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada', 'descricao': 'Função que realiza a validação do texto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-483"></a>

## validar_UNID

Valida um valor de UNID utilizando uma função de texto.

Esta função valida um valor de UNID (Unidade) chamando outra função `validar_texto` para garantir que o valor esteja dentro dos critérios especificados, incluindo uma restrição máxima de comprimento de 1000 caracteres.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. Se não for válido, a função `validar_texto` lançará uma exceção.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1000)
```

</details>

---

<a id="funcao-484"></a>

## validar_cd

Valida se um valor pertence ao domínio definido por ValoresTUC.

Verifica se o valor fornecido está dentro do domínio permitido pela classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_cd(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não pertence ao domínio da variável.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cd(cls, value):
        if not ValoresTUC.teste(int(value)):
            raise ValueError(f'{value} não pertence ao domínio da variável.\n')
        return value
```

</details>

---

<a id="funcao-485"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a uma máxima extensão de 10 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-486"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-487"></a>

## validar_CC

Valida um número de cartão de crédito (CC) utilizando uma função auxiliar.

A função valida o valor fornecido como um número de cartão de crédito, verificando se ele atende a determinados critérios definidos em outra função chamada `validar_texto`. O parâmetro `info.field_name` é usado para obter o nome do campo que está sendo validado.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usada em métodos de classe). |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente um número de cartão de crédito. |
| `info` | `Não especificado` | Informações sobre o campo que está sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função `validar_texto`, que é responsável por realizar a validação específica do número de cartão de crédito.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=9)
```

</details>

---

<a id="funcao-488"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a 25 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou lança uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-489"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-490"></a>

## validar_IND

Valida um valor específico de acordo com regras definidas.

A função valida se o valor fornecido é uma string de comprimento máximo 1 e pertence ao domínio ['C', 'D']. Utiliza a função `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_IND(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['C','D'])
```

</details>

---

<a id="funcao-491"></a>

## validar_Dt

Valida uma data, permitindo que o valor seja vazio.

Esta função utiliza um validador de campo para verificar se a data fornecida é válida. Ela aceita tanto datas como valores vazios, conforme especificado pelo parâmetro `vazio=True` no chamada à função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma data. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value, vazio=True)
```

</details>

---

<a id="funcao-492"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-493"></a>

## validar_CC

Valida um valor de cartão de crédito (CC) utilizando uma função auxiliar.

A função valida o valor do cartão de crédito, verificando se ele atende a determinados critérios definidos em outra função chamada 'validar_texto'. O parâmetro 'max_len' é fixado em 50, indicando que o comprimento máximo aceitável para o valor é de 50 caracteres.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usado em métodos de classe). |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função 'validar_texto'.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Método de validação do Pydantic.'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada', 'descricao': 'Função auxiliar que realiza a validação do texto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
```

</details>

---

<a id="funcao-494"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-495"></a>

## validar_IND

Valida um valor específico de acordo com regras definidas.

A função valida se o valor fornecido é uma string de comprimento máximo 1 e pertence ao domínio ['N', 'E', 'X']. Utiliza a função `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_IND(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['N','E','X'])
```

</details>

---

<a id="funcao-496"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-497"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-498"></a>

## validar_hist

Valida um valor de histórico.

Utiliza uma validação de texto para garantir que o valor do histórico não exceda a largura máxima permitida (65535 caracteres).

### Assinatura

```python
def validar_hist(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual. |
| `value` | `Não especificado` | Valor do histórico a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_hist(cls, value, info):
        return validar_texto(value, info.field_name, max_len=65535)
```

</details>

---

<a id="funcao-499"></a>

## validar_CC

Valida um número de cartão de crédito (CC).

Verifica se o valor fornecido é uma string que representa um número de cartão de crédito válido, com no máximo 15 caracteres.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado, presumivelmente uma string. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, lança uma exceção.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=15)
```

</details>

---

<a id="funcao-500"></a>

## validar_UNID

Valida um valor de UNID (Unidade) utilizando uma função de validação de texto.

A função valida o valor fornecido, verificando se ele é um texto válido e limitado a 25 caracteres. Utiliza uma função auxiliar chamada `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_UNID(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou lança uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UNID(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-501"></a>

## validar_NUM

Valida um valor de texto com base em regras específicas.

A função valida um valor de texto, verificando se ele atende a determinados critérios, incluindo uma restrição de comprimento máximo.

### Assinatura

```python
def validar_NUM(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_NUM(cls, value, info):
        return validar_texto(value, info.field_name, max_len=50)
```

</details>

---

<a id="funcao-502"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-503"></a>

## validar_IND

Valida um valor específico de acordo com regras definidas.

A função valida se o valor fornecido é uma string de comprimento máximo 1 e pertence ao domínio ['C', 'D']. Utiliza a função `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_IND(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_IND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=1, dominio=['C','D'])
```

</details>

---

<a id="funcao-504"></a>

## validar_vl

Valida um valor como decimal, garantindo que seja maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor é um número decimal e se ele é maior ou igual a zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-505"></a>

## validar_CC

Valida um valor de cartão de crédito (CC) utilizando uma função de validação de texto.

A função valida o valor do cartão de crédito, verificando se ele atende aos critérios definidos em 'validar_texto'. O parâmetro 'max_len' é fixado em 25, limitando a quantidade máxima de caracteres permitidos no valor do CC.

### Assinatura

```python
def validar_CC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do cartão de crédito a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo, como seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor retornado pela função 'validar_texto'.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import', 'descricao': 'Método de validação do Pydantic.'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada', 'descricao': 'Função que realiza a validação do texto.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_CC(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-506"></a>

## validar_ide

Valida se um valor é um inteiro e maior que zero.

A função valida se o valor fornecido é um número inteiro e se ele é maior que zero. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_ide(cls, v, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `v` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, v, info):
        return validar_inteiro(v, info.field_name, min_val=1)
```

</details>

---

<a id="funcao-507"></a>

## validar_Dt

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de campo para verificar a validade da data fornecida. A implementação específica do validador é realizada pela função `validar_data`.

### Assinatura

```python
def validar_Dt(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_data']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_Dt(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-508"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

Verifica se o valor fornecido atende aos critérios definidos pela função `ValoresTI.teste` e lança uma exceção caso contrário.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como TI. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        if not ValoresTI.teste(int(value)):
            raise ValueError(f'O dado não é válido como TI.\n')
        return value
```

</details>

---

<a id="funcao-509"></a>

## validar_cds

Valida um valor de acordo com regras específicas para CDS.

A função valida um valor utilizando uma validação de texto, permitindo valores vazios e limitando a sua comprimento máximo em 25 caracteres. Esta função é usada como um decorador de validação em classes Pydantic.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-510"></a>

## validar_vl_cdng

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido é um inteiro e está entre 1 e 6, inclusive. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def validar_vl_cdng(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_cdng(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=6)
```

</details>

---

<a id="funcao-511"></a>

## validar_vl_tpajst

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido está entre 1 e 12, inclusos. Utiliza uma validação de inteiro para garantir que o valor seja um número inteiro válido no intervalo especificado.

### Assinatura

```python
def validar_vl_tpajst(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se estiver dentro do intervalo especificado. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_tpajst(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=12)
```

</details>

---

<a id="funcao-512"></a>

## validar_vl

Valida um valor utilizando uma função de validação decimal.

Esta função utiliza um validador decimal para verificar a validade do valor fornecido. É parte de uma classe que pode ter mais métodos de validação definidos.

### Assinatura

```python
def validar_vl(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que o método é definido. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for válido. O tipo exato depende da implementação de `validar_decimal`.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl(cls, value):
        return validar_decimal(value)
```

</details>

---

<a id="funcao-513"></a>

## validar_datas

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de dados para verificar a validade da data fornecida. Ela é chamada como método de classe, o que sugere que pode ser parte de uma classe maior com lógica de validação de dados.

### Assinatura

```python
def validar_datas(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que a função é definida. Normalmente, este parâmetro não é usado dentro da função. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_datas(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-514"></a>

## validar_vl_voc

Valida se um valor é decimal e não negativo.

A função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e maior ou igual a zero.

### Assinatura

```python
def validar_vl_voc(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_voc(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-515"></a>

## valida_nr_ax

Valida se um valor é um número inteiro entre 0 e 99.

A função valida que o valor fornecido é um número inteiro dentro do intervalo de 0 a 99, inclusive. Utiliza uma validação personalizada definida em outra parte do código (presumivelmente em 'validar_inteiro').

### Assinatura

```python
def valida_nr_ax(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def valida_nr_ax(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0, max_val=99)
```

</details>

---

<a id="funcao-516"></a>

## validar_dig_inc

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_dig_inc(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_dig_inc(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-517"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-518"></a>

## valida_textos

Valida um texto com base em regras específicas.

A função valida um valor de texto, verificando se ele está vazio e limitando sua comprimento máximo. Utiliza uma validação personalizada definida em outra parte do código.

### Assinatura

```python
def valida_textos(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def valida_textos(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=1000)
```

</details>

---

<a id="funcao-519"></a>

## validar_UND

Valida um valor de acordo com regras específicas para uma UNidade de Negócio (UND).

A função utiliza um validador de texto personalizado para verificar se o valor fornecido atende aos critérios de comprimento máximo definidos.

### Assinatura

```python
def validar_UND(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UND(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-520"></a>

## validar_UAR

Valida se o valor é uma UAR, TUC ou UC.

A função valida que o valor fornecido seja um dos códigos específicos ('UAR', 'TUC', 'UC') e também verifica se ele atende aos critérios de texto definidos em outra função chamada `validar_texto`.

### Assinatura

```python
def validar_UAR(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de dados. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_UAR(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['UAR','TUC','UC'])
```

</details>

---

<a id="funcao-521"></a>

## validar_cds

Valida um valor de acordo com regras específicas para campos de texto em um modelo Pydantic.

A função valida o valor fornecido, considerando se está vazio e limitando sua comprimento máximo. Utiliza uma validação interna definida por outra função chamada `validar_texto`.

### Assinatura

```python
def validar_cds(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cds(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=25)
```

</details>

---

<a id="funcao-522"></a>

## validar_TUC

Valida se um valor é um código de Unidade Curricular (UC) válido.

A função valida que o valor seja um número inteiro entre 99 e 999, e que atenda a uma condição específica definida pela classe ValoresTUC. Caso contrário, lança uma exceção ValueError.

### Assinatura

```python
def validar_TUC(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual (geralmente usada em métodos de validação de modelos Pydantic). |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado (geralmente fornecido automaticamente pelo Pydantic). |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é um código de UC válido.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TUC(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=99, max_val=999)
        if (num != None) and (num != '') and (not ValoresTUC.teste(int(value))):
            raise ValueError(f'O dado não é válido como código de UC.\n')
        return value
```

</details>

---

<a id="funcao-523"></a>

## validar_TI

Valida se um valor é válido como TI (Tipo de Identificação).

A função valida se o valor fornecido está dentro do intervalo de 1 a 100 e se atende aos critérios específicos definidos pela classe ValoresTI. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_TI(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário, lança uma exceção.

### Exceções

- **`ValueError`**: Quando o valor não é válido como TI.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_TI(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=100)
        if not ValoresTI.teste(int(value)):
           raise ValueError(f'O dado não é válido como TI.\n')
        return value
```

</details>

---

<a id="funcao-524"></a>

## validar_vl_tpajst

Valida um valor de acordo com regras específicas.

A função valida se o valor fornecido é uma string que atende a determinados critérios, incluindo comprimento máximo e domínio de valores permitidos.

### Assinatura

```python
def validar_vl_tpajst(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que contém o campo a ser validado. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou lança uma exceção se a validação falhar.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_tpajst(cls, value, info):
        return validar_texto(value, info.field_name, max_len=3, dominio = ['BRR','BAR'])
```

</details>

---

<a id="funcao-525"></a>

## silenciador_de_erros

Silencia erros de validação e registra-os em um objeto.

Tenta executar uma função de manipulação (handler) e silencia quaisquer erros de validação. Se ocorrer um erro, captura-o, registra os erros no objeto e retorna o objeto com a lista de erros associada.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método silenciador_de_erros. |
| `values` | `any` | Valores a serem manipulados pela função handler. |
| `handler` | `Não especificado` | Função que realiza a manipulação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Objeto com os erros de validação registrados, ou o resultado da função handler se não houver erros.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução do handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            errors_list = e.errors()
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", errors_list)
            return obj_com_erro
```

</details>

---

<a id="funcao-526"></a>

## pipeline_validacao_completa

Executa um pipeline de validação completo para uma tabela de dados.

Este método percorre cada linha da tabela, identifica erros e aplica regras de negócios específicas. Caso encontre erros, os consolida e lança uma exceção de validação.

### Assinatura

```python
def pipeline_validacao_completa(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela de dados. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atualizada se não houver erros. Caso contrário, lança uma exceção de validação.

### Exceções

- **`ValidationError`**: Quando ocorrem erros durante a validação dos dados.

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def pipeline_validacao_completa(self):
        raw_data = self.tabela 
        erros_consolidados = []

        for i, obj in enumerate(raw_data):
            
            try:
                linha_id = getattr(obj, 'Ide_AIS', f'Linha_{i+1}')
            except:
                linha_id = f'Linha_{i+1}'

            if hasattr(obj, "_erros_registro") and obj._erros_registro:
                for err in obj._erros_registro:
                    if isinstance(err['loc'], str): 
                        loc_tuple = (err['loc'],)
                    else:
                        loc_tuple = tuple(err['loc'])
                    
                    err['loc'] = ('tabela', i+1) + loc_tuple
                    err['msg'] = f"[Estrutura] {err['msg']}"
                    
                    if err.get('type') not in ['value_error', 'type_error', 'missing', 'int_parsing', 'float_parsing']:
                        err['type'] = PydanticCustomError('value_error', err['msg'])  
                    erros_consolidados.append(err)

            v_ti  = getattr(obj, 'Nr_TI', None)
            v_tuc = getattr(obj, 'Nr_TUC', None)
            v_cc  = getattr(obj, 'Cd_CC', None)
            v_cm  = getattr(obj, 'Nr_CM', None)
            v_a1  = getattr(obj, 'Nr_A1', None)
            v_a2  = getattr(obj, 'Nr_A2', None)
            v_a3  = getattr(obj, 'Nr_A3', None)
            v_a4  = getattr(obj, 'Nr_A4', None)
            v_a5  = getattr(obj, 'Nr_A5', None)
            v_a6  = getattr(obj, 'Nr_A6', None)
            v_dt_IMB  = getattr(obj, 'Dt_Imob', None)
            v_UND = getattr(obj, 'Cd_UND_AIS', None)
            v_Cd_UAR = getattr(obj, 'Cd_UAR', None)
            v_QTD = getattr(obj, 'Qtd_AIS', None)

            def check(func, campo, *args):
                try:
                    func(*args)
                except Exception as e:
                    erros_consolidados.append({
                        "type": "value_error",
                        "loc": ("tabela", i+1, campo),
                        "msg": f"[Regra Negocio] [ID: {linha_id}] {str(e)}",
                        "input": getattr(obj, campo, "N/A"),
                        "ctx": {'error': ValueError(str(e))}
                    })

            try:
                check(validar_tuc_ti, "Nr_TUC", v_tuc, v_ti, linha_id, v_a1)
                check(validar_tucs_proibidos, "Nr_TUC", v_tuc, linha_id)
                check(validar_administracao, "Cd_CC", v_ti, v_cc, linha_id)
                check(validar_cm, "Nr_CM", v_ti, v_cm, linha_id)
                check(validar_ti_distribuicao, "Nr_TI", v_ti, linha_id)
                check(validar_cabos, "Nr_TUC", v_tuc, v_a1, v_a3, v_a4, v_a5, v_UND, linha_id)
                check(validar_torre_poste, "Nr_TI", v_ti, v_tuc, v_a1, linha_id)
                check(validar_bem_individual, "Nr_TUC", v_ti, v_tuc, v_a1, v_a2, v_a3, v_a4, v_a5, v_a6, v_QTD, linha_id, v_Cd_UAR)

            except Exception as e_critico:
                erros_consolidados.append({
                    "type": "value_error",
                    "loc": ("tabela", i+1),
                    "msg": f"[ERRO CRÍTICO] Falha na linha {linha_id}: {str(e_critico)}",
                    "input": {},
                    "ctx": {'error': ValueError(str(e_critico))}
                })
                continue

        if erros_consolidados:
            raise ValidationError.from_exception_data(self.__class__.__name__, erros_consolidados)
        return self
```

</details>

---

<a id="funcao-527"></a>

## validar_datas

Valida um valor de data no formato específico.

A função valida se o valor fornecido é uma string representando uma data no formato 'DD-MM-AAAA'. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_datas(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, esperando-se uma string representando uma data. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_datas(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=7)
```

</details>

---

<a id="funcao-528"></a>

## validar_valores_e_horas

Valida se um valor é decimal e maior ou igual a zero.

A função utiliza um validador de campo para verificar se o valor fornecido é um número decimal e se ele é maior ou igual a zero. Se não for, uma exceção será lançada.

### Assinatura

```python
def validar_valores_e_horas(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser um número decimal. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_valores_e_horas(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-529"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-530"></a>

## valida_txt_ativ_exec

Valida um texto conforme regras específicas.

A função valida um valor de texto, garantindo que ele não esteja vazio e que seu comprimento não exceda 2000 caracteres. Utiliza uma validação personalizada definida em outro lugar no código.

### Assinatura

```python
def valida_txt_ativ_exec(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`
- `{'nome': 'validar_texto', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def valida_txt_ativ_exec(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=2000)
```

</details>

---

<a id="funcao-531"></a>

## valida_txt_obs

Valida um texto observação conforme regras específicas.

Realiza a validação de um texto observação, permitindo que seja vazio e limitando sua extensão máxima em 65000 caracteres.

### Assinatura

```python
def valida_txt_obs(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado, que deve ser um texto observação. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def valida_txt_obs(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=65000)
```

</details>

---

<a id="funcao-532"></a>

## valida_dsc_cargo

Valida o texto de um campo de cargo.

Verifica se o valor fornecido é um texto válido para um campo de cargo, garantindo que não esteja vazio e que tenha uma comprimento máximo de 255 caracteres.

### Assinatura

```python
def valida_dsc_cargo(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

Valor validado, se for válido. Caso contrário, levanta uma exceção.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def valida_dsc_cargo(cls, value, info):
        return validar_texto(value, info.field_name, vazio=False, max_len=255)
```

</details>

---

<a id="funcao-533"></a>

## validar_campos_texto_25

Valida se um campo de texto não excede 25 caracteres.

Esta função valida que o valor fornecido para um campo de texto não ultrapassa a quantidade máxima de 25 caracteres. Utiliza uma validação personalizada definida em outra parte do código, passando o nome do campo e o valor atual como parâmetros.

### Assinatura

```python
def validar_campos_texto_25(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a validação. |
| `value` | `Não especificado` | Valor do campo de texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_campos_texto_25(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-534"></a>

## validar_cod_ccus

Valida um código CCUS (Código de Controle de Usuário) conforme regras específicas.

A função valida o valor fornecido como um código CCUS, verificando se ele é uma string não vazia com no máximo 25 caracteres. Utiliza a função `validar_texto` para realizar a validação.

### Assinatura

```python
def validar_cod_ccus(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado como código CCUS. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cod_ccus(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25, vazio=True)
```

</details>

---

<a id="funcao-535"></a>

## validar_ind_fl

Valida um valor como código de tipo de folha.

Verifica se o valor é um número inteiro entre 1 e 7, e se é válido conforme a classe ValoresTUC. Caso contrário, lança uma exceção.

### Assinatura

```python
def validar_ind_fl(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, caso contrário lança uma exceção.

### Exceções

- **`ValueError`**: Quando o dado não é válido como código de tipo de folha.

### Dependências

- `pydantic.field_validator`
- `ValoresTUC.teste`
- `ValueError`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ind_fl(cls, value, info):
        num = validar_inteiro(value, info.field_name, min_val=1, max_val=7)

        if num not in (None, "") and not ValoresTUC.teste(int(value)):
            raise ValueError("O dado não é válido como código de tipo de folha.")

        return value
```

</details>

---

<a id="funcao-536"></a>

## silenciador_de_erros

Silencia erros de validação e registra-os em um objeto.

Tenta executar uma função de manipulação (handler) e silencia quaisquer erros de validação. Se ocorrer um erro, captura-o, registra os erros no objeto e retorna o objeto com a lista de erros associada.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método silenciador_de_erros. |
| `values` | `any` | Valores a serem manipulados pela função handler. |
| `handler` | `Não especificado` | Função que realiza a manipulação dos valores. |

### Retorno

**Tipo:** `Não especificado`

Objeto com os erros de validação registrados, ou o resultado da função handler se não houver erros.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução do handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            errors_list = e.errors()
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", errors_list)
            return obj_com_erro
```

</details>

---

<a id="funcao-537"></a>

## erros

Valida e normaliza os dados de uma tabela, identificando erros e regras de negócio.

A função percorre cada objeto na tabela, verifica erros em campos específicos e aplica regras de negócios. Se encontrar erros, lança uma exceção com detalhes dos problemas encontrados.

### Assinatura

```python
def erros(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela de dados. |

### Retorno

**Tipo:** `Não especificado`

A instância atualizada, se não houver erros. Caso contrário, lança uma exceção.

### Exceções

- **`ValidationError`**: Quando encontrados erros na tabela de dados.

### Dependências

- `{'nome': 'decimal.Decimal', 'categoria': 'import', 'descricao': 'Utilizado para manipulação de números decimais.'}`
- `{'nome': 'pydantic.ValidationError', 'categoria': 'import', 'descricao': 'Exceção utilizada para representar erros de validação.'}`
- `{'nome': 're.fullmatch', 'categoria': 'chamada', 'descricao': 'Função usada para verificar se uma string corresponde a um padrão regular.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def erros(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_FOPAG", f"Linha_{i+1}")
            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                                **err,
                                "loc": ("tabela", i, *loc),
                                "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                            })

            def erro(campo, msg):
                erros.append({
                                "type": "value_error",
                                "loc": ("tabela", i, campo),
                                "msg": f"[Regra Negócio] [ID: {linha_id}] {msg}",
                                "input": getattr(obj, campo, None),
                                "ctx": {"error": ValueError(msg)},
                            })

            def dec(campo):
                val = getattr(obj, campo, None)
                if val in (None, ""):
                    return None
                try:
                    return Decimal(str(val).replace(",", "."))
                except Exception:
                    return None

            def soma_igual(total, partes, nome):
                v_total = dec(total)
                v_partes = [dec(c) for c in partes]

                if v_total is None or any(v is None for v in v_partes):
                    return

                soma = sum(v_partes, Decimal("0"))
                tolerancia = abs(v_total) * Decimal("0.01")

                if abs(v_total - soma) > tolerancia:
                    erro(
                            total,
                            f"{nome} inconsistente. {total} deve ser igual à soma de "
                            f"{' + '.join(partes)}. Informado: {v_total}; calculado: {soma}."
                        )

            dt_cmpt = getattr(obj, "Dt_CMPT", None)
            if not isinstance(dt_cmpt, str) or not re.fullmatch(r"\d{4}/(0[1-9]|1[0-2])", dt_cmpt):
                erro(
                        "Dt_CMPT",
                        "Dt_CMPT deve estar no formato aaaa/mm, por exemplo 2024/06."
                    )

            campos_horas = ["Hr_Efetivas", "Hr_CAPEX", "Hr_OPEX", "Hr_ODD"]

            for campo in campos_horas:
                v = dec(campo)
                if v is not None and v < 0:
                    erro(campo, f"{campo} não pode conter valor negativo.")

            soma_igual(
                            "Hr_Efetivas",
                            ["Hr_CAPEX", "Hr_OPEX"],
                            "Horas efetivas"
                        )

            hr_odd = dec("Hr_ODD")
            hr_opex = dec("Hr_OPEX")

            if hr_odd is not None and hr_opex is not None and hr_odd > hr_opex:
                erro("Hr_ODD", "Hr_ODD deve ser menor ou igual a Hr_OPEX.")

            hr_efetivas = dec("Hr_Efetivas")

            if hr_efetivas is not None and hr_efetivas != Decimal("44"):
                erro(
                        "Hr_Efetivas",
                        "Hr_Efetivas, em tese, deve corresponder a 44 horas semanais, nos termos gerais da CLT. "
                        "Caso haja jornada diversa, deve ser apresentada convenção, acordo coletivo ou justificativa aplicável."
                    )

            campos_valores = [
                                "VL_FOPAG",
                                "VL_FOPAG_CAPEX",
                                "VL_FOPAG_OPEX",
                                "VL_FOPAG_ODD",
                            ]

            for campo in campos_valores:
                v = dec(campo)
                if v is not None and v < 0:
                    erro(campo, f"{campo} não pode conter valor negativo.")

            soma_igual(
                            "VL_FOPAG",
                            ["VL_FOPAG_CAPEX", "VL_FOPAG_OPEX"],
                            "Valor da folha"
                        )

            vl_odd = dec("VL_FOPAG_ODD")
            vl_opex = dec("VL_FOPAG_OPEX")

            if vl_odd is not None and vl_opex is not None and vl_odd > vl_opex:
                erro(
                        "VL_FOPAG_ODD",
                        "VL_FOPAG_ODD deve ser menor ou igual a VL_FOPAG_OPEX."
                    )

        if erros:
            raise ValidationError.from_exception_data(
                                                        self.__class__.__name__,
                                                        erros
                                                    )

        return self
```

</details>

---

<a id="funcao-538"></a>

## validar_vl_rubr

Valida se um valor é um decimal e está dentro de um intervalo mínimo.

A função valida que o valor fornecido é um número decimal e verifica se ele está acima do valor mínimo especificado (padrão é 0).

### Assinatura

```python
def validar_vl_rubr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser um número decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, levantando uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-539"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe atual, geralmente usada em métodos de validação dentro de classes Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado, se for um inteiro não negativo. Caso contrário, uma exceção será levantada.

### Dependências

- `{'nome': 'pydantic.field_validator', 'tipo': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-540"></a>

## validar_cod_rubrica

Valida se um valor pertence a uma lista específica de códigos rubricas.

A função verifica se o valor fornecido está presente na lista de códigos rubricas definida no atributo `CODIGOS_RUBRICAS` da classe. Se o valor não estiver presente, lança um erro de validação.

### Assinatura

```python
def validar_cod_rubrica(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a lista de códigos rubricas. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de validação, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cod_rubrica(cls, value, info):
        return validar_lista(value, cls.CODIGOS_RUBRICAS, info.field_name, vazio=False)
```

</details>

---

<a id="funcao-541"></a>

## validar_ind_rubr

Valida se um valor está dentro de um intervalo específico.

A função valida que o valor fornecido está entre 1 e 3, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro válido nesse intervalo.

### Assinatura

```python
def validar_ind_rubr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele passar na validação.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ind_rubr(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-542"></a>

## silenciador_de_erros

Silencia erros de validação, capturando e armazenando-os em um objeto.

Executa uma função de manipulação (handler) e silencia quaisquer erros de validação que possam ocorrer. Se ocorrer um erro, o valor original é convertido em um objeto do modelo especificado pela classe (cls), e os erros são armazenados no atributo `_erros_registro` desse objeto.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que será usada para construir o objeto com erros. |
| `values` | `any` | Valor ou objeto que será passado para a função de manipulação (handler). |
| `handler` | `Não especificado` | Função que será chamada com o valor fornecido. Deve ser capaz de lidar com erros de validação. |

### Retorno

**Tipo:** `Não especificado`

O objeto original ou um novo objeto do modelo Pydantic com os erros armazenados.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução da função handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro
```

</details>

---

<a id="funcao-543"></a>

## validar_tabela

Valida uma tabela de objetos, coletando e lançando erros.

Itera sobre cada objeto na tabela, verifica erros associados a cada um e os agrupa. Se houver erros, lança uma exceção de validação com detalhes dos mesmos.

### Assinatura

```python
def validar_tabela(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela a ser validada. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atual se não houver erros de validação.

### Exceções

- **`pydantic.ValidationError`**: Quando há erros de validação na tabela.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_RUB", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
```

</details>

---

<a id="funcao-544"></a>

## validar_vl_rubr

Valida se um valor é um decimal e está dentro de um intervalo mínimo.

A função valida que o valor fornecido é um número decimal e verifica se ele está acima do limite mínimo especificado (padrão é 0).

### Assinatura

```python
def validar_vl_rubr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado, deve ser um número decimal. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, levantando uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0)
```

</details>

---

<a id="funcao-545"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-546"></a>

## validar_cod_rubrica

Valida se o valor fornecido é uma lista de códigos ST válidos.

A função valida que o valor passado seja uma lista contendo apenas códigos ST (Subtipos de Tributo) permitidos, conforme definidos na classe. Caso contrário, lança uma exceção de validação.

### Assinatura

```python
def validar_cod_rubrica(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a definição dos códigos ST válidos. |
| `value` | `Não especificado` | Valor a ser validado, que deve ser uma lista de códigos ST. |
| `info` | `Não especificado` | Informações adicionais sobre o campo sendo validado, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cod_rubrica(cls, value, info):
        return validar_lista(value, cls.CODIGOS_ST, info.field_name, vazio=False)
```

</details>

---

<a id="funcao-547"></a>

## validar_ind_rubr

Valida se um valor está dentro de um intervalo específico para indicadores de rubricas.

A função valida que o valor fornecido esteja entre 1 e 3, inclusos. Utiliza uma validação interna para garantir que o valor seja um inteiro válido nesse intervalo.

### Assinatura

```python
def validar_ind_rubr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido; caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_inteiro`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ind_rubr(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-548"></a>

## silenciador_de_erros

Silencia erros de validação, capturando e armazenando-os em um objeto.

Executa uma função de manipulação (handler) e silencia quaisquer erros de validação que possam ocorrer. Se ocorrer um erro, o valor original é convertido em um objeto do modelo especificado pela classe (cls), e os erros são armazenados no atributo `_erros_registro` desse objeto.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que será usada para construir o objeto com erros. |
| `values` | `any` | Valor ou objeto que será passado para a função de manipulação (handler). |
| `handler` | `Não especificado` | Função que será chamada com o valor fornecido. Deve ser capaz de lidar com erros de validação. |

### Retorno

**Tipo:** `Não especificado`

O objeto original ou um novo objeto do modelo Pydantic com os erros armazenados.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução da função handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro
```

</details>

---

<a id="funcao-549"></a>

## validar_tabela

Valida uma tabela de objetos, coletando e lançando erros.

Itera sobre cada objeto na tabela, verifica erros associados a cada um e os agrupa. Se houver erros, lança uma exceção de validação com detalhes dos mesmos.

### Assinatura

```python
def validar_tabela(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela a ser validada. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atual se não houver erros de validação.

### Exceções

- **`pydantic.ValidationError`**: Quando há erros de validação na tabela.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
```

</details>

---

<a id="funcao-550"></a>

## validar_datas

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de dados para verificar a validade da data fornecida. Ela é chamada como método de classe, o que sugere que pode ser parte de uma classe maior com lógica de validação de dados.

### Assinatura

```python
def validar_datas(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que a função é definida. É um parâmetro padrão do Python para métodos de classe. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_datas(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-551"></a>

## validar_vl_rubr

Valida se um valor está dentro de um intervalo decimal específico.

A função valida que o valor fornecido esteja entre 0 e 1, inclusos. Utiliza uma validação decimal para garantir a precisão do número.

### Assinatura

```python
def validar_vl_rubr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele estiver dentro do intervalo válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-552"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-553"></a>

## validar_cod_rubrica

Valida se um valor é um inteiro dentro de um intervalo específico.

A função valida que o valor fornecido é um número inteiro e está contido no intervalo definido por min_val e max_val. Se não for, lança uma exceção.

### Assinatura

```python
def validar_cod_rubrica(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que possui o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados que está sendo validado. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_inteiro']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cod_rubrica(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=1, max_val=3)
```

</details>

---

<a id="funcao-554"></a>

## validar_ind_rubr

Valida um valor de rubrica em conformidade com regras específicas.

A função valida o valor de uma rubrica, garantindo que ele seja um texto não vazio e cuja comprimento máximo seja de 25 caracteres. Utiliza a validação interna do Pydantic para realizar essa verificação.

### Assinatura

```python
def validar_ind_rubr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da rubrica a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ind_rubr(cls, value, info):
        return validar_texto(value, info.field_name, max_len=25)
```

</details>

---

<a id="funcao-555"></a>

## validar_text

Valida um texto com base em regras específicas.

A função valida um valor de texto, utilizando uma validação personalizada definida em outra função chamada 'validar_texto'. A validação inclui o nome do campo e um limite máximo de caracteres (padrão é 20).

### Assinatura

```python
def validar_text(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_text(cls, value, info):
        return validar_texto(value, info.field_name, max_len=20)
```

</details>

---

<a id="funcao-556"></a>

## validar_text1

Valida um texto com base em regras específicas.

A função valida um valor de texto, utilizando uma função auxiliar `validar_texto`, e retorna o resultado da validação. A validação inclui verificar se o campo está vazio e limitar a sua comprimento máximo.

### Assinatura

```python
def validar_text1(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor do campo a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_text1(cls, value, info):
        return validar_texto(value, info.field_name, max_len=10)
```

</details>

---

<a id="funcao-557"></a>

## validar_text2

Valida um texto com base em regras específicas.

A função valida um valor de texto, utilizando uma validação personalizada definida em outra função chamada 'validar_texto'. A validação inclui o nome do campo e um limite máximo de caracteres (255).

### Assinatura

```python
def validar_text2(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém a função de validação. |
| `value` | `Não especificado` | Valor do texto a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo, incluindo seu nome. |

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_text2(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-558"></a>

## silenciador_de_erros

Silencia erros de validação, capturando e armazenando-os em um objeto.

Executa uma função de manipulação (handler) e silencia quaisquer erros de validação que possam ocorrer. Se ocorrer um erro, o valor original é convertido em um objeto do modelo especificado pela classe (cls), e os erros são armazenados no atributo `_erros_registro` desse objeto.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que será usada para construir o objeto com erros. |
| `values` | `any` | Valor ou objeto que será passado para a função de manipulação (handler). |
| `handler` | `Não especificado` | Função que será chamada com o valor fornecido. Deve ser capaz de lidar com erros de validação. |

### Retorno

**Tipo:** `Não especificado`

O objeto original ou um novo objeto do modelo Pydantic com os erros armazenados.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução da função handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro
```

</details>

---

<a id="funcao-559"></a>

## validar_tabela

Valida uma tabela de objetos, coletando e lançando erros.

Itera sobre cada objeto na tabela, verifica erros associados a cada um e os agrupa. Se houver erros, lança uma exceção de validação com detalhes dos mesmos.

### Assinatura

```python
def validar_tabela(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela a ser validada. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atual se não houver erros de validação.

### Exceções

- **`pydantic.ValidationError`**: Quando há erros de validação na tabela.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
```

</details>

---

<a id="funcao-560"></a>

## validar_datas

Valida uma data utilizando um validador específico.

Esta função utiliza um validador de dados para verificar a validade da data fornecida. Ela é chamada como método de classe, o que sugere que pode ser parte de uma classe maior com lógica de validação de dados.

### Assinatura

```python
def validar_datas(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe em que a função é definida. É um parâmetro padrão do Python para métodos de classe. |
| `value` | `Não especificado` | Valor da data a ser validado. |

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_datas(cls, value):
        return validar_data(value)
```

</details>

---

<a id="funcao-561"></a>

## validar_vl_rubr

Valida se um valor está dentro de um intervalo decimal específico.

A função valida que o valor fornecido esteja entre 0 e 1, inclusos. Utiliza uma validação decimal para garantir a precisão do número.

### Assinatura

```python
def validar_vl_rubr(cls, value):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor a ser validado. |

### Retorno

**Tipo:** `Não especificado`

O valor original se ele estiver dentro do intervalo válido, ou lança uma exceção caso contrário.

### Dependências

- `pydantic.field_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_vl_rubr(cls, value):
        return validar_decimal(value, min_val=0, max_val=1)
```

</details>

---

<a id="funcao-562"></a>

## validar_ide

Valida se um valor é um inteiro não negativo.

A função valida que o valor fornecido é um número inteiro e maior ou igual a zero. Utiliza uma validação interna para garantir que o valor atenda aos critérios especificados.

### Assinatura

```python
def validar_ide(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado. |
| `info` | `Não especificado` | Informações sobre o campo de dados. |

### Retorno

**Tipo:** `Não especificado`

O valor original se for válido, ou lança uma exceção caso contrário.

### Dependências

- `{'nome': 'pydantic.field_validator', 'categoria': 'import'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ide(cls, value, info):
        return validar_inteiro(value, info.field_name, min_val=0)
```

</details>

---

<a id="funcao-563"></a>

## validar_cod_rubrica

Valida um código de rubrica conforme regras específicas.

A função valida o valor fornecido como código de rubrica, permitindo valores vazios e limitando a sua extensão máxima em 255 caracteres. Utiliza uma validação interna para garantir que o valor atenda aos critérios definidos.

### Assinatura

```python
def validar_cod_rubrica(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic. |
| `value` | `Não especificado` | Valor a ser validado como código de rubrica. |
| `info` | `Não especificado` | Informações sobre o campo sendo validado, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor validado ou uma exceção se a validação falhar.

### Dependências

- `{'imports': ['pydantic.field_validator'], 'chamadas': ['field_validator', 'validar_texto']}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_cod_rubrica(cls, value, info):
        return validar_texto(value, info.field_name, vazio=True, max_len=255)
```

</details>

---

<a id="funcao-564"></a>

## validar_ind_rubr

Valida um valor de rubrica em conformidade com regras específicas.

A função valida o valor de uma rubrica, garantindo que ele seja um texto não vazio e que seu comprimento esteja dentro do limite máximo de 255 caracteres. Utiliza a validação de texto definida na função `validar_texto`.

### Assinatura

```python
def validar_ind_rubr(cls, value, info):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe que contém o método de validação. |
| `value` | `Não especificado` | Valor da rubrica a ser validado. |
| `info` | `Não especificado` | Informações adicionais sobre o campo de validação, incluindo seu nome. |

### Retorno

**Tipo:** `Não especificado`

O valor original da rubrica se a validação for bem-sucedida. Caso contrário, uma exceção será levantada.

### Dependências

- `pydantic.field_validator`
- `validar_texto`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_ind_rubr(cls, value, info):
        return validar_texto(value, info.field_name, max_len=255)
```

</details>

---

<a id="funcao-565"></a>

## silenciador_de_erros

Silencia erros de validação, capturando e armazenando-os em um objeto.

Executa uma função de manipulação (handler) e silencia quaisquer erros de validação que possam ocorrer. Se ocorrer um erro, o valor original é convertido em um objeto do modelo especificado pela classe (cls), e os erros são armazenados no atributo `_erros_registro` desse objeto.

### Assinatura

```python
def silenciador_de_erros(cls, values: any, handler):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `cls` | `Não especificado` | Classe do modelo Pydantic que será usada para construir o objeto com erros. |
| `values` | `any` | Valor ou objeto que será passado para a função de manipulação (handler). |
| `handler` | `Não especificado` | Função que será chamada com o valor fornecido. Deve ser capaz de lidar com erros de validação. |

### Retorno

**Tipo:** `Não especificado`

O objeto original ou um novo objeto do modelo Pydantic com os erros armazenados.

### Exceções

- **`ValidationError`**: Quando ocorre um erro de validação durante a execução da função handler.

### Dependências

- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def silenciador_de_erros(cls, values: any, handler):
        try:
            return handler(values)
        except ValidationError as e:
            dados = values if isinstance(values, dict) else values.__dict__
            obj_com_erro = cls.model_construct(**dados)
            object.__setattr__(obj_com_erro, "_erros_registro", e.errors())
            return obj_com_erro
```

</details>

---

<a id="funcao-566"></a>

## validar_tabela

Valida uma tabela de objetos, coletando e lançando erros.

Itera sobre cada objeto na tabela, verifica erros associados a cada um e os agrupa. Se houver erros, lança uma exceção de validação com detalhes dos mesmos.

### Assinatura

```python
def validar_tabela(self):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `self` | `Não especificado` | Instância da classe que contém a tabela a ser validada. |

### Retorno

**Tipo:** `Não especificado`

Retorna a instância atual se não houver erros de validação.

### Exceções

- **`pydantic.ValidationError`**: Quando há erros de validação na tabela.

### Dependências

- `pydantic.ValidationError`
- `pydantic.model_validator`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tabela(self):
        erros = []

        for i, obj in enumerate(self.tabela):
            linha_id = getattr(obj, "Id_Ext_MOP_ITEM", f"Linha_{i+1}")

            for err in getattr(obj, "_erros_registro", []):
                loc = err.get("loc", ())
                if isinstance(loc, str):
                    loc = (loc,)

                erros.append({
                    **err,
                    "loc": ("tabela", i, *loc),
                    "msg": f"[Estrutura] [ID: {linha_id}] {err.get('msg')}",
                })

        if erros:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                erros
            )

        return self
```

</details>

---

<a id="funcao-567"></a>

## adicionar

Adiciona um erro de validação à lista de erros.

Cria e adiciona um dicionário representando um erro de validação à lista `erros`. O erro contém informações sobre o tipo, a localização, o valor do campo e a mensagem de erro específica.

### Assinatura

```python
def adicionar(campo, mensagem):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo que gerou o erro. |
| `mensagem` | `Não especificado` | Mensagem de erro específica a ser incluída no dicionário do erro. |

### Dependências

- `imports`
- `chamadas`

<details>
<summary>Visualizar código-fonte</summary>

```python
def adicionar(campo, mensagem):
            erros.append({
                            'type': 'value_error',
                            'loc': (campo,),
                            'input': getattr(self, campo),
                            'ctx': {'error': ValueError(mensagem)},
                        })
```

</details>

---

<a id="funcao-568"></a>

## to_date

Converte um valor em uma data no formato 'YYYY/MM/DD'.

Tenta converter o valor fornecido para uma data no formato 'YYYY/MM/DD'. Se o valor for vazio ou não puder ser convertido, retorna a data padrão de 1º de janeiro de 1920.

### Assinatura

```python
def to_date(v):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `v` | `Não especificado` | Valor que será convertido em uma data. |

### Retorno

**Tipo:** `datetime.date`

Data no formato 'YYYY/MM/DD' ou a data padrão de 1º de janeiro de 1920 se o valor não for válido.

### Exceções

- **`Exception`**: Caso ocorra qualquer erro durante a conversão da data.

### Dependências

- `datetime.date`
- `datetime.datetime`

<details>
<summary>Visualizar código-fonte</summary>

```python
def to_date(v):
            if not v or str(v).strip() == "":
                return date(1920, 1, 1)
            try:
                return datetime.strptime(str(v).strip(), "%Y/%m/%d").date()
            except Exception:
                return date(1920, 1, 1)
```

</details>

---

<a id="funcao-569"></a>

## obter

Obtém o valor de um campo específico de um objeto.

Retorna o valor do atributo especificado em 'campo' do objeto 'result'. Se o campo não existir, retorna o valor padrão fornecido (None se nenhum padrão for especificado).

### Assinatura

```python
def obter(campo, padrao=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do atributo a ser obtido. |
| `padrao` | `Não especificado` | Valor padrão retornado se o campo não existir no objeto. |

### Retorno

**Tipo:** `Não especificado`

Valor do atributo ou valor padrão.

### Dependências

- `getattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def obter(campo, padrao=None):
            return getattr(result, campo, padrao)
```

</details>

---

<a id="funcao-570"></a>

## esta_vazio

Verifica se um valor é vazio.

Determina se o valor fornecido é considerado vazio, que pode ser `None`, uma string vazia ou uma string com apenas espaços em branco.

### Assinatura

```python
def esta_vazio(valor):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser verificado. |

### Retorno

**Tipo:** `bool`

True se o valor é vazio, False caso contrário.

### Dependências

- `isinstance`

<details>
<summary>Visualizar código-fonte</summary>

```python
def esta_vazio(valor):
            return (
                        valor is None
                        or (
                            isinstance(valor, str)
                            and valor.strip() == ""
                        )
                    )
```

</details>

---

<a id="funcao-571"></a>

## adicionar_erro

Adiciona um erro de valor a uma lista global.

Esta função adiciona um erro de valor à lista `erros`. O erro contém informações sobre o campo, a mensagem de erro e o valor associado.

### Assinatura

```python
def adicionar_erro(campo, mensagem, valor=None):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | O nome do campo onde ocorreu o erro. |
| `mensagem` | `Não especificado` | A mensagem de erro a ser adicionada. |
| `valor` | `Não especificado` | O valor associado ao campo onde ocorreu o erro. Se não for fornecido, será `None`. |

### Dependências

- `{'tipo': 'ValueError', 'categoria': 'chamada'}`
- `{'nome': 'erros', 'categoria': 'externa'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def adicionar_erro(campo, mensagem, valor=None):
            erros.append({
                            "type": "value_error",
                            "loc": (campo,),
                            "input": valor,
                            "ctx": {
                                "error": ValueError(mensagem)
                            }
                        })
```

</details>

---

<a id="funcao-572"></a>

## converter_decimal

Converte um valor para decimal.

Tenta converter o valor fornecido em um número de ponto flutuante. Se o valor for vazio, retorna 0.0. Caso contrário, remove espaços em branco e substitui vírgulas por pontos antes da conversão. Em caso de erro de tipo ou valor, adiciona um erro ao campo especificado e retorna None.

### Assinatura

```python
def converter_decimal(valor, campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `valor` | `Não especificado` | Valor a ser convertido em decimal. |
| `campo` | `Não especificado` | Nome do campo onde ocorreu o erro, caso haja. |

### Retorno

**Tipo:** `Não especificado`

Valor convertido em decimal ou None em caso de erro.

### Exceções

- **`TypeError`**: Quando o valor não pode ser convertido para string.
- **`ValueError`**: Quando a conversão de string para float falha.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def converter_decimal(valor, campo):
            if esta_vazio(valor):
                return 0.0

            try:
                return float(
                                str(valor).strip().replace(",", ".")
                            )

            except (TypeError, ValueError):
                adicionar_erro(
                                    campo,
                                    f"Valor decimal inválido: {valor!r}",
                                    valor
                                )
                return None
```

</details>

---

<a id="funcao-573"></a>

## texto

Obtém o valor de um campo específico de um objeto e retorna uma string formatada.

A função busca o valor do atributo especificado em um objeto chamado 'resultado'. Se o valor for None, retorna uma string vazia. Caso contrário, converte o valor para string e remove espaços em branco no início e fim.

### Assinatura

```python
def texto(campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do atributo a ser recuperado do objeto 'resultado'. |

### Retorno

**Tipo:** `Não especificado`

Valor formatado como string, ou uma string vazia se o valor for None.

### Dependências

- `getattr`
- `str`
- `strip`

<details>
<summary>Visualizar código-fonte</summary>

```python
def texto(campo):
            valor = getattr(resultado, campo, None)
            return "" if valor is None else str(valor).strip()
```

</details>

---

<a id="funcao-574"></a>

## validar_tp_bem

Valida se o tipo de bem (TP_BEM) é '4' quando há enquadramento específico em TI, TUC ou CC.

A função verifica se os valores de TI, TUC e CC correspondem a certos padrões. Se houver um enquadramento e TP_BEM não for '4', uma exceção ValueError é levantada com detalhes do motivo do erro.

### Assinatura

```python
def validar_tp_bem(ti, tuc, cc, tp_bem, linha):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `ti` | `Não especificado` | Número de identificação da TI. |
| `tuc` | `Não especificado` | Número de identificação da TUC. |
| `cc` | `Não especificado` | Código do centro de custo (CC). |
| `tp_bem` | `Não especificado` | Tipo de bem. |
| `linha` | `Não especificado` | Número da linha atual no contexto do processamento. |

### Exceções

- **`ValueError`**: Quando TP_BEM não é '4' e há enquadramento em TI, TUC ou CC.

### Dependências

- `re`

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_tp_bem(ti, tuc, cc, tp_bem, linha):
            try:
                ti_num = int(ti)
            except (ValueError, TypeError):
                ti_num = None
            try:
                tuc_num = int(tuc)
            except (ValueError, TypeError):
                tuc_num = None

            tp_bem = str(tp_bem).strip()
            cc = str(cc).strip()

            motivos = []

            if ti_num is not None and (
                                            70 <= ti_num <= 91
                                            or ti_num in {94, 95, 97, 99}
                                        ):
                motivos.append(f"Nr_TI={ti}")

            if tuc_num in {230, 235, 535}:
                motivos.append(f"Nr_TUC={tuc}")

            if re.fullmatch(r"1232\d0\d05", cc):
                motivos.append(f"Cd_CC={cc} (veículos)")

            if motivos and tp_bem != "4":
                raise ValueError(
                    f"Id_SEQ_INC={linha}: TP_BEM esperava-se ser 4 "
                    f"quando houver enquadramento em "
                    f"{', '.join(motivos)}. "
                    f"Valor informado: TP_BEM={tp_bem}."
                )
```

</details>

---

<a id="funcao-575"></a>

## validar_voc_ca_avaliacao_2

Valida a avaliação de voz e conteúdo (VOC-CA) para um tipo específico.

Verifica se o tipo de avaliação é '2' e se o valor da VOC-CA não é zero. Lança uma exceção caso contrário.

### Assinatura

```python
def validar_voc_ca_avaliacao_2(tp_aval, voc_ca, com_voc, linha):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `tp_aval` | `Não especificado` | Tipo de avaliação. |
| `voc_ca` | `Não especificado` | Valor da VOC-CA. |
| `com_voc` | `Não especificado` | Comentário relacionado à VOC-CA. |
| `linha` | `Não especificado` | Número da linha correspondente ao registro. |

### Exceções

- **`ValueError`**: Quando o tipo de avaliação é '2' e o valor da VOC-CA é zero.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_voc_ca_avaliacao_2(tp_aval, voc_ca, com_voc, linha):
            if str(tp_aval).strip() != "2":
                return
            try:
                valor_ca = float(voc_ca)
            except (TypeError, ValueError):
                return

            if float(valor_ca) == 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Para Cd_TP_AVAL=2, "
                    "VL_VOC_CA não pode ser zero. "
                    f"VL_COM_VOC={com_voc}; VL_VOC_CA={voc_ca}."
                )
```

</details>

---

<a id="funcao-576"></a>

## validar_pct_oe

Valida se o percentual de OE (Operações Especiais) é maior que zero quando pelo menos uma das flags FLG_DOA_OE, FLG_INCOR_OE ou FLG_PLPT_OE está ativa.

A função verifica se pelo menos uma das flags FLG_DOA_OE, FLG_INCOR_OE ou FLG_PLPT_OE está ativa. Se sim, valida se o percentual de OE (pct_oe) é maior que zero. Caso contrário, a função não faz nada.

### Assinatura

```python
def validar_pct_oe(flg_doa, flg_incor, flg_plpt, pct_oe, linha):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `flg_doa` | `Não especificado` | Flag indicando se DOA_OE está ativa. |
| `flg_incor` | `Não especificado` | Flag indicando se INCOR_OE está ativa. |
| `flg_plpt` | `Não especificado` | Flag indicando se PLPT_OE está ativa. |
| `pct_oe` | `Não especificado` | Percentual de OE a ser validado. |
| `linha` | `Não especificado` | Número da linha atual, usado para identificar o erro. |

### Exceções

- **`ValueError`**: Quando pelo menos uma das flags está ativa e pct_oe não é maior que zero.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def validar_pct_oe(flg_doa, flg_incor, flg_plpt, pct_oe, linha):

            flags = {
                        "FLG_DOA_OE": flg_doa,
                        "FLG_INCOR_OE": flg_incor,
                        "FLG_PLPT_OE": flg_plpt
                    }

            flags_ativas = [
                                campo
                                for campo, valor in flags.items()
                                if str(valor).strip() == "1"
                            ]

            if (not flags_ativas):
                return

            try:
                percentual = float(str(pct_oe).strip().replace(",", "."))
            except (ValueError, TypeError):
                return
            
            if not percentual > 0:
                raise ValueError(
                    f"Id_SEQ_INC={linha}: Pct_OE deve ser maior que zero "
                    f"quando pelo menos um dos indicadores "
                    f"{', '.join(flags_ativas)} for igual a 1. "
                    f"Valor informado: Pct_OE={pct_oe}."
                )
```

</details>

---

<a id="funcao-577"></a>

## executar

Executa uma função se nenhuma dependência estiver na lista de inválidos.

Verifica se qualquer dependência fornecida está na lista de inválidos. Se não estiver, a função é chamada com os argumentos fornecidos. Caso contrário, nada é feito. Qualquer exceção lançada pela função é capturada e armazenada em uma lista de erros.

### Assinatura

```python
def executar(campo, dependencias, funcao, *args):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo ou chave associado aos dados. |
| `dependencias` | `Não especificado` | Lista de dependências que devem ser verificadas. |
| `funcao` | `Não especificado` | Função a ser executada se nenhuma dependência estiver inválida. |
| `args` | `Não especificado` | Argumentos posicionais passados para a função. |

### Exceções

- **`ValueError, TypeError, ArithmeticError`**: Exceções que podem ser lançadas pela função e capturadas para armazenamento.

### Dependências

Nenhuma dependência externa documentada.

<details>
<summary>Visualizar código-fonte</summary>

```python
def executar(campo, dependencias, funcao, *args):
            if any(dep in invalidos for dep in dependencias):
                return
            try:
                funcao(*args)
            except (ValueError, TypeError, ArithmeticError) as exc:
                mensagem = str(exc).strip()
                erros.append({
                                "type": "value_error",
                                "loc": (campo,),
                                "input": getattr(resultado, campo, None),
                                "ctx": {"error": ValueError(mensagem)},
                            })
```

</details>

---

<a id="funcao-578"></a>

## check

Executa uma função e captura quaisquer exceções lançadas, consolidando-as em um formato específico.

A função `check` executa a função fornecida (`func`) com os argumentos variádicos (`*args`). Se ocorrer uma exceção durante a execução da função, ela é capturada e armazenada em uma lista chamada `erros_consolidados`. O erro é consolidado em um dicionário contendo informações sobre o tipo de erro, a localização do erro, a mensagem de erro, o valor de entrada que causou o erro e o contexto da exceção.

### Assinatura

```python
def check(func, campo, *args):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `func` | `Não especificado` | Função a ser executada. |
| `campo` | `Não especificado` | Nome do campo associado ao erro. |
| `args` | `Não especificado` | Argumentos variádicos a serem passados para a função `func`. |

### Dependências

- `{'nome': 'ValueError', 'tipo': 'built-in', 'categoria': 'import'}`
- `{'nome': 'erros_consolidados.append', 'tipo': 'variável global', 'categoria': 'chamada'}`
- `{'nome': 'func', 'tipo': None, 'categoria': 'chamada'}`
- `{'nome': 'getattr', 'tipo': 'built-in', 'categoria': 'chamada'}`
- `{'nome': 'str', 'tipo': 'built-in', 'categoria': 'chamada'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def check(func, campo, *args):
                try:
                    func(*args)
                except Exception as e:
                    erros_consolidados.append({
                        "type": "value_error",
                        "loc": ("tabela", i+1, campo),
                        "msg": f"[Regra Negocio] [ID: {linha_id}] {str(e)}",
                        "input": getattr(obj, campo, "N/A"),
                        "ctx": {'error': ValueError(str(e))}
                    })
```

</details>

---

<a id="funcao-579"></a>

## erro

Adiciona um erro de validação a uma lista chamada 'erros'.

Esta função adiciona um dicionário representando um erro de validação à lista 'erros'. O erro contém informações sobre o tipo do erro, a localização no contexto da tabela e mensagem personalizada.

### Assinatura

```python
def erro(campo, msg):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo que gerou o erro. |
| `msg` | `Não especificado` | Mensagem de erro personalizada. |

### Dependências

- `ValueError`
- `erros.append`
- `getattr`

<details>
<summary>Visualizar código-fonte</summary>

```python
def erro(campo, msg):
                erros.append({
                                "type": "value_error",
                                "loc": ("tabela", i, campo),
                                "msg": f"[Regra Negócio] [ID: {linha_id}] {msg}",
                                "input": getattr(obj, campo, None),
                                "ctx": {"error": ValueError(msg)},
                            })
```

</details>

---

<a id="funcao-580"></a>

## dec

Converte um valor de campo em uma instância de Decimal.

A função tenta converter o valor do campo especificado em um objeto Decimal, substituindo vírgulas por pontos. Se o valor for None ou vazio, a função retorna None. Caso ocorra qualquer exceção durante a conversão, também é retornado None.

### Assinatura

```python
def dec(campo):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `campo` | `Não especificado` | Nome do campo cujo valor será convertido em Decimal. |

### Retorno

**Tipo:** `Decimal`

Valor convertido em Decimal ou None se a conversão falhar.

### Dependências

- `decimal.Decimal`

<details>
<summary>Visualizar código-fonte</summary>

```python
def dec(campo):
                val = getattr(obj, campo, None)
                if val in (None, ""):
                    return None
                try:
                    return Decimal(str(val).replace(",", "."))
                except Exception:
                    return None
```

</details>

---

<a id="funcao-581"></a>

## soma_igual

Verifica se a soma de partes é igual ao valor total, considerando uma tolerância.

A função compara a soma das partes com o valor total, aceitando uma margem de erro definida por 1% do valor total. Se houver inconsistência, uma mensagem de erro é gerada.

### Assinatura

```python
def soma_igual(total, partes, nome):
```

### Parâmetros

| Nome | Tipo | Descrição |
|---|---|---|
| `total` | `Não especificado` | Valor total a ser comparado com a soma das partes. |
| `partes` | `Não especificado` | Lista de valores que serão somados e comparados com o valor total. |
| `nome` | `Não especificado` | Nome do contexto ou identificador para a mensagem de erro, se houver. |

### Retorno

**Tipo:** `Não especificado`

A função não retorna um valor explícito. Em caso de inconsistência, uma mensagem de erro é gerada.

### Dependências

- `{'nome': 'decimal.Decimal', 'categoria': 'import', 'descricao': 'Utilizado para manipulação de números decimais com precisão.'}`

<details>
<summary>Visualizar código-fonte</summary>

```python
def soma_igual(total, partes, nome):
                v_total = dec(total)
                v_partes = [dec(c) for c in partes]

                if v_total is None or any(v is None for v in v_partes):
                    return

                soma = sum(v_partes, Decimal("0"))
                tolerancia = abs(v_total) * Decimal("0.01")

                if abs(v_total - soma) > tolerancia:
                    erro(
                            total,
                            f"{nome} inconsistente. {total} deve ser igual à soma de "
                            f"{' + '.join(partes)}. Informado: {v_total}; calculado: {soma}."
                        )
```

</details>

---
