#ifndef _BOOT_LOADER_
#define _BOOT_LOADER_

#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include<stdbool.h>
#include "main.h"
#include "CommandCodes.h"

#define FLASH_BASE_USER_APP 0x08008000
#define RX_BUFFER_LENGTH 200


void jump_to_bootloader();
void jump_to_user_application();
void bl_handle_get_version(uint8_t *rx_buffer);
void bl_handle_get_help(uint8_t *rx_buffer);
void bl_send_ack(uint8_t length);
void bl_send_nack();
bool bl_verify_crc(uint8_t *pBuff,uint32_t len,uint32_t host_crc);
void bl_uart_write_data(uint8_t *pbuff,uint32_t len);
uint8_t bl_get_version();
#endif