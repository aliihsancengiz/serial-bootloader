#include "../Inc/Bootloader.h"

uint8_t rx_buffer[RX_BUFFER_LENGTH];
uint8_t tx_get_version[]="BL_GET_VERSION\r\n";
uint8_t tx_get_help[]="BL_GET_HELP\r\n";
uint8_t tx_unknown[]="UNKNOWN COMMAND\r\n";

extern UART_HandleTypeDef huart2;
extern CRC_HandleTypeDef hcrc;
uint8_t supported_cmd[]={BL_GET_VERSION,BL_GET_HELP,BL_GET_CID,BL_GET_RDP_STATUS,BL_GO_TO_ADDR,BL_FLASH_ERASE,BL_MEM_WRITE};

void jump_to_bootloader()
{
    volatile uint8_t recv_len=0;
    while(1)
    {
        // Clear the buffer
        memset(rx_buffer,0,200);
        // Read one byte which indicates lengths of command
        HAL_UART_Receive(&huart2,rx_buffer,1,HAL_MAX_DELAY);
        // Extract length of received command
        recv_len=(uint8_t)((int)(rx_buffer[0]));  
        // Get command from host
        HAL_UART_Receive(&huart2,&rx_buffer[1],recv_len,HAL_MAX_DELAY);
        switch(((int)rx_buffer[1]))
        {
            case BL_GET_VERSION:
                bl_handle_get_version(rx_buffer);
                break;
            case BL_GET_HELP:
                bl_handle_get_help(rx_buffer);
                break;
            case BL_GET_CID:
                bl_handle_get_cid(rx_buffer);
                break;
            case BL_GET_RDP_STATUS:
                bl_handle_get_rdp(rx_buffer);
                break;
            case BL_GO_TO_ADDR:
                bl_handle_go_to_adress(rx_buffer);
            default:
                break;
        }
    }
}

void jump_to_user_application()
{
    // Function pointer for jumping user app
    void (*app_reset_handler)(void);
    uint32_t msp_value=*(volatile uint32_t*)FLASH_BASE_USER_APP;
    __set_MSP(msp_value);
    uint32_t reset_handler_adress=*(volatile uint32_t*)(FLASH_BASE_USER_APP+4);
    app_reset_handler=(void*)reset_handler_adress;
    app_reset_handler();

}
void bl_send_ack(uint8_t length)
{
    uint8_t ackbuff[15];
    memset(ackbuff,0,15);
    sprintf(ackbuff,"-%d-%d-\r\n",BL_ACK,length);
    HAL_UART_Transmit(&huart2,ackbuff,strlen((const char *)ackbuff),HAL_MAX_DELAY);
}
void bl_send_nack()
{
    uint8_t nackbuff[10];
    memset(nackbuff,0,10);
    sprintf((char*)nackbuff,"-%d-\r\n",BL_NACK);
    HAL_UART_Transmit(&huart2,&nackbuff,strlen((const char *)nackbuff),HAL_MAX_DELAY);
}
uint32_t bytes2word(uint8_t buff[])
{
	uint32_t val=0;
	int i;
	for(i=0;i<4;i++)
	{
		val=val|(((int)buff[i])<<(8*i));
	}
	return val;
}
bool bl_verify_crc(uint8_t *pBuff,uint32_t len,uint32_t host_crc)
{
    uint32_t i;
    uint32_t xxACC=0xff;
    for ( i = 0; i < len; i++)
    {
        uint32_t ins_data=pBuff[i];
        xxACC=HAL_CRC_Accumulate(&hcrc,&ins_data,1);
    }
    __HAL_CRC_DR_RESET(&hcrc);
    if(xxACC==host_crc)
    {
        return 1;
    }
    else
    {
        return 0;
    }
    
}
uint8_t bl_get_version()
{
    return (uint8_t)BL_VERSION;
}
void bl_uart_write_data(uint8_t *pbuff,uint32_t len)
{
    HAL_UART_Transmit(&huart2,pbuff,len,HAL_MAX_DELAY);
}
uint16_t read_cid()
{
    return ((uint16_t)DBGMCU->IDCODE  & 0x0FFF); 
}
uint8_t read_rdp_level()
{
    volatile uint32_t *pOP=(uint32_t*)(0x1FFFC000);
    return (uint8_t)(*pOP >> 8);
}
void bl_handle_get_version(uint8_t *rx_buffer)
{
    uint8_t bl_version[]="Version 1.0\r\n";
    uint8_t crc_buff[4];
    crc_buff[0]=(int)rx_buffer[2];
    crc_buff[1]=(int)rx_buffer[3];
    crc_buff[2]=(int)rx_buffer[4];
    crc_buff[3]=(int)rx_buffer[5];
    volatile uint32_t host_crc=bytes2word(crc_buff);
    if(bl_verify_crc(&rx_buffer[0],2,host_crc))
    {
        bl_send_ack(1);
        bl_uart_write_data(bl_version,strlen((const char *)bl_version));
    }
    else
    {
        bl_send_nack();
    }
    
}
void bl_handle_get_help(uint8_t *rx_buffer)
{
    uint8_t crc_buff[4],scmd_buff[40],i;
    
    crc_buff[0]=(int)rx_buffer[2];
    crc_buff[1]=(int)rx_buffer[3];
    crc_buff[2]=(int)rx_buffer[4];
    crc_buff[3]=(int)rx_buffer[5];
    volatile uint32_t host_crc=bytes2word(crc_buff);
    sprintf(scmd_buff,"-%d-%d-%d-%d-%d-%d-%d-\r\n",supported_cmd[0],supported_cmd[1],supported_cmd[2],supported_cmd[3],supported_cmd[4],supported_cmd[5],supported_cmd[6]);
    if(bl_verify_crc(&rx_buffer[0],2,host_crc))
    {
        bl_send_ack(1);
        bl_uart_write_data(scmd_buff,sizeof(scmd_buff));
    }
    else
    {
        bl_send_nack();
    }
}
void bl_handle_get_cid(uint8_t *rx_buffer)
{
    uint8_t crc_buff[4],cid_buff[10];
    crc_buff[0]=(int)rx_buffer[2];
    crc_buff[1]=(int)rx_buffer[3];
    crc_buff[2]=(int)rx_buffer[4];
    crc_buff[3]=(int)rx_buffer[5];
    volatile uint32_t host_crc=bytes2word(crc_buff);
    uint16_t cid=read_cid();
    sprintf(cid_buff,"-%d-\r\n",cid);
    if(bl_verify_crc(&rx_buffer[0],2,host_crc))
    {
        bl_send_ack(1);
        bl_uart_write_data(cid_buff,strlen((const char *)cid_buff));
    }
    else
    {
        bl_send_nack();
    }
}
void bl_handle_get_rdp(uint8_t *rx_buffer)
{
    uint8_t crc_buff[4],rdp_buff[10];
    crc_buff[0]=(int)rx_buffer[2];
    crc_buff[1]=(int)rx_buffer[3];
    crc_buff[2]=(int)rx_buffer[4];
    crc_buff[3]=(int)rx_buffer[5];
    volatile uint32_t host_crc=bytes2word(crc_buff);
    volatile uint8_t rdp_status=read_rdp_level();
    sprintf(rdp_buff,"-%d-\r\n",rdp_status);
    if(bl_verify_crc(&rx_buffer[0],2,host_crc))
    {
        bl_send_ack(1);
        bl_uart_write_data(rdp_buff,strlen((const char *)rdp_buff));
    }
    else
    {
        bl_send_nack();
    }
}

void bl_handle_go_to_adress(uint8_t *rx_buffer)
{
    uint8_t crc_buffer[4],adress[4],reply_to_cmd[20];
    crc_buffer[0]=(int)rx_buffer[6];
    crc_buffer[1]=(int)rx_buffer[7];
    crc_buffer[2]=(int)rx_buffer[8];
    crc_buffer[3]=(int)rx_buffer[9];
    adress[0]=(int)rx_buffer[2];
    adress[1]=(int)rx_buffer[3];
    adress[2]=(int)rx_buffer[4];
    adress[3]=(int)rx_buffer[5];
    volatile uint32_t host_crc=bytes2word(crc_buffer);
    volatile uint32_t adress_to_jump=bytes2word(adress);
    if(bl_verify_crc(&rx_buffer[0],6,host_crc))
    {
        sprintf(reply_to_cmd,"-Okey i am running-\r\n");
        bl_send_ack(1);
        bl_uart_write_data(reply_to_cmd,strlen((const char *)reply_to_cmd));
        adress_to_jump+=1;
        void (*lets_jump)(void)=(void*)adress_to_jump;
        lets_jump();
    }
    else
    {
        sprintf(reply_to_cmd,"-CRC is not good-\r\n");
        bl_send_nack();
        bl_uart_write_data(reply_to_cmd,strlen((const char *)reply_to_cmd));
    }
}