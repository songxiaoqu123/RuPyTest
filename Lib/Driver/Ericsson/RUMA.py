import logging
import re
import numpy
import sys
import os
import clr
import time
#import System
# clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Bin\Ruma\Release\TigerApplicationServiceClient.dll')
# clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Bin\Ruma\Release\TSLControlClient.dll')
#clr.AddReference('C:\Program Files (x86)\Ericsson\RUMA\Bin\Ruma\Release\RumaControlClient.dll')
clr.AddReference('C:\Program Files (x86)\Ericsson\RUMA\Bin\Ruma\Release\RumaToolControl.dll')
#clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Ruma\RumaControlClient.dll')#some version installer under this folder, need ...
from Tiger.Ruma import *


moudle_logger = logging.getLogger(__name__+'.TCA()')

class TCA():
    def __init__(self):
        # if 1:
        #     clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Bin\Ruma\Release\TigerApplicationServiceClient.dll')
        #     clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Bin\Ruma\Release\TSLControlClient.dll')
        #     clr.AddReference('C:\Program Files (x86)\Ericsson\TCA\Bin\Ruma\Release\RumaControlClient.dll')
        #
        # else:
        #     clr.AddReference('C:\Program Files\Ericsson\TCA\Ruma\TigerApplicationServiceClient.dll')
        #     clr.AddReference('C:\Program Files\Ericsson\TCA\Ruma\TSLControlClient.dll')
        #     clr.AddReference('C:\Program Files\Ericsson\TCA\Ruma\RumaControlClient.dll')

        self.rumaClient = RumaControlClientFactory.CreateDefault()
        #time.sleep(60), delay 60s maybe needed if the first time swith on the Ct10
        # self.SetLineRate(cpriPorts='1A',lineRate='LR9_8')
        # time.sleep(0.1)
        # self.SetCpriVersion(cpriPorts='1A',version='VER2')
        self.SetMemoryMode()
        self.SetprotocoversionAndSetCascade()
        # self.lineRate = LineRate.LR9_8
        # self.rumaClient.CpriConfig.SetLineRate('1A',self.lineRate)
        # time.sleep(0.5)
        # self.version = CpriVersion.VERSION_2
        # self.rumaClient.CpriConfig.SetCpriVersion('1A', self.version)
        # print('LineRate.LR9_8',' CpriVersion.VERSION_2')
        moudle_logger.debug("Initialize the TCA,->RumaControlClientFactory.CreateDefault(),->SetMemoryMode()->SetprotocoversionAndSetCascade()")

    def delete(self):
        moudle_logger.debug('tca is destructed.')
        RumaControlClientFactory.StopDefaultTool()


    def GetAllocatedCpriPorts(self):
        Ports=self.rumaClient.CpriConfig.GetAllocatedCpriPorts()
        moudle_logger.debug('AllocatedCpriPorts:'+str(Ports))
        return Ports

    def GetCt10info(self):
        info=[]
        info.append(self.rumaClient.RuMaUtilities.GetUsbDevice())
        info.append(self.rumaClient.RuMaUtilities.GetProductInfo())
        info.append(self.rumaClient.RuMaUtilities.GetFPGAVersion(0))
        info.append(self.rumaClient.RuMaUtilities.GetFPGAVersion(1))
        moudle_logger.debug(str(info))
        return info

    def SetprotocoversionAndSetCascade(self,protRev=3,cascW=1,timSyncOn=1,enChain=1,cpriPorts='1A'):
        self.rumaClient.CpriConfig.SetRevision(cpriPorts, protRev)
        self.rumaClient.CpriConfig.SetCascade(cpriPorts, cascW, timSyncOn, enChain)

    def SetMemoryMode(self):
        self.rumaClient.HardwareControl.HardwareControlSetMemoryMode(HardwareMemoryMode.CPRI)

    def TransFlowDirection(self,InPara='TX'):
        if InPara=='TX':
            InPara=CpriFlowDirection.TX
        elif InPara=='RX':
            InPara=CpriFlowDirection.RX
        return InPara

    def TransFlowDataType(self,InPara):
        if InPara=='IQ':
            InPara = FlowDataType.IQ
        elif InPara=='AXC':
            InPara = FlowDataType.AXC
        elif InPara=='ECP':
            InPara = FlowDataType.ECP
        elif InPara=='NONE':
            InPara = FlowDataType.NONE
        return InPara

    def TransFlowDataMode(self,InPara='Carrier'):
        if InPara=='RAW':
            InPara=FlowDataMode.RAW
        elif InPara=='Carrier':
            InPara=FlowDataMode.Carrier
        return InPara

    #IQ/AXC play button status , running or stop
    def GetOneFlowState(self,cpriPorts,flowDirection,flowDataType):
        flowDirection = self.TransFlowDirection(flowDirection)
        flowDataType = self.TransFlowDataType(flowDataType)
        status=self.rumaClient.CpriDataFlow.GetOneFlowState(cpriPorts, flowDirection, flowDataType, False)
        #print(flowDirection,flowDataType,status,'GetOneFlowState')
        return status

    #function for what?
    def SetDebugManipulationInfo(self,cpriPorts,carrierIndex):
        debugManip = DebugManipulationInfo
        debugManip.DebugEnabled = False
        for i in carrierIndex:
            self.rumaClient.CarrierConfig.SetDebugManipulationInfo(cpriPorts, carrierIndex(i), debugManip)

    # lineRate values : LR1_2,LR2_5,LR4_9,LR9_8
    def SetLineRate(self,cpriPorts='1A',lineRate='LR9_8'):
        moudle_logger.info('lineRate='+str(lineRate))
        if (lineRate=='LR2_5') or (lineRate=='2or.5'):
            lineRate = LineRate.LR2_5
        elif (lineRate=='LR4_9') or (lineRate=='4.9'):
            lineRate = LineRate.LR4_9
        elif (lineRate=='LR9_8') or (lineRate=='9.8'):
            lineRate = LineRate.LR9_8
        elif (lineRate=='LR10_1') or (lineRate=='10.1'):
            lineRate = LineRate.LR10_1
        else:
            print('lineRate not supported. Supported values: ''LR1_2'',''LR2_5'',''LR4_9'',''LR9_8''')
        self.rumaClient.CpriConfig.SetLineRate(cpriPorts,lineRate)


    def SetCpriVersion(self,cpriPorts='1A',version='VER2'):
        print('version=',version)
        if version=='VERSION_1' or  version=='V1' or version=='VER1':
            version = CpriVersion.VERSION_1
        elif version=='VERSION_2' or  version=='V2' or version=='VER2':
            version = CpriVersion.VERSION_2
        else:
            print('lineRate not supported. Supported values: ''VERSION_1'',''VERSION_2''')
        self.rumaClient.CpriConfig.SetCpriVersion(cpriPorts, version)


    def SetScramblingSeed(self,cpriPorts='1A',seed=0):
        self.rumaClient.CpriConfig.SetScramblingSeed(cpriPorts,seed)


    def GetSfpStatus(self,cpriPorts='1A'):
        self.rumaClient.CpriConfig.GetSfpStatus(cpriPorts)

    def GetStatus(self,cpriPorts='1A'):
        statusTCA=self.rumaClient.CpriConfig.GetLinkState(cpriPorts)
        return statusTCA
    def SetStatusEnable(self,cpriPorts='1A'):
        self.rumaClient.CpriConfig.SetLinkState(cpriPorts, CpriLinkState.CPRI_LINK_STATE_ENABLE)

    def SetStatusDiable(self,cpriPorts='1A'):
        self.rumaClient.CpriConfig.SetLinkState(cpriPorts, CpriLinkState.CPRI_LINK_STATE_DISABLE)

    def ClearAllAlarmCounters(self,cpriPorts='1A'):
        self.rumaClient.CpriConfig.ClearAllAlarmCounters(cpriPorts)

    #??
    def GetAlarmsFlagged(self,cpriPorts='1A'):
        cpriAlarm=self.rumaClient.CpriConfig.GetAlarmsFlagged(cpriPorts,CpriReuseAlarms.CPRI_TRX_CPRI_FSM_NOT_STATE_F)
        return cpriAlarm

    def SetCpriLink(self,version,rate,seed,cpriPorts='1A'):
            self.SetCpriVersion(cpriPorts,version)
            self.SetLineRate(cpriPorts,rate)
            self.SetScramblingSeed(cpriPorts,seed)

    def SetCpriMode(self,cpriPorts='1A',mode='MasterRec'):
        #  Mode values : MasterRec,MasterRe,SecondarySlave,PrimarySlave
        # if mode=='MasterRec':
        #     mode = LineRate.LR2_5
        if mode=='MasterRe':
            mode = CpriMode.MasterRec
        elif mode=='LR4_9':
            mode = CpriMode.MasterRe
        elif mode=='SecondarySlave':
            mode = CpriMode.SecondarySlave
        elif mode=='PrimarySlave':
            mode = CpriMode.PrimarySlave
        else:
            print('lineRate not supported. Supported values: ''LR1_2'',''LR2_5'',''LR4_9'',''LR9_8''')
        self.rumaClient.CpriConfig.SetLineRate(cpriPorts,mode)

    def GetFlowDirection(self,flowDirection='TX'):
        if flowDirection=='TX':
            flowDirection = CpriFlowDirection.TX
        if flowDirection=='RX':
            flowDirection = CpriFlowDirection.RX
        return(flowDirection)


    def TX_add_carrier(self,cpriPorts='1A',axc_cont=0,carrier_id=1,tech='LTE',freq=15360 ,fs_hf=149,fs_bf=216,fs_adr=1,Gain=0):
        flowDirection = CpriFlowDirection.TX
        if freq==960:
            cr_sr = SampleFrequency.Frequency_0_96
        elif freq==3840:
            cr_sr = SampleFrequency.Frequency_3_84
        elif freq==7680:
            cr_sr = SampleFrequency.Frequency_7_68
        elif freq==15360:
            cr_sr = SampleFrequency.Frequency_15_36
        elif freq == 23040:
            cr_sr = SampleFrequency.Frequency_23_04
        elif freq==30720:
            cr_sr = SampleFrequency.Frequency_30_72
        else:
            print('No such sample rate',freq)

        if tech=='GSM':
            cr_rat = Technology.GSM
        elif tech=='WCDMA_5_BIT':
            cr_rat =Technology.WCDMA_5_BIT
        elif tech=='LTE':
            cr_rat = Technology.LTE
        elif tech=='CDMA':
            cr_rat = Technology.CDMA
        elif tech=='WCDMA_7_BIT':
            cr_rat = Technology.WCDMA_7_BIT
        else:
            print('No such Technology',tech)

        dummy1 = int(1);dummy2 = ''

        (cr_nr)=self.rumaClient.CarrierConfig.AddCarrier(cpriPorts,flowDirection, carrier_id, axc_cont, cr_sr, cr_rat,dummy1,dummy2)
        print('cpriPorts=',cpriPorts,'flowDirection:TX=',flowDirection,' carrier_id',carrier_id,' axc_cont=',axc_cont,' cr_sr=',cr_sr,' cr_rat=',cr_rat,'   Return value=',cr_nr)
        moudle_logger.debug('  cpriPorts='+str(cpriPorts)+'  flowDirection:TX='+str(flowDirection)+'  carrier_id'+str(carrier_id)+'  axc_cont='+str(axc_cont)+' cr_sr='+str(cr_sr)+'  cr_rat='+str(cr_rat)+'   Return value='+str(cr_nr))
        tcaCarrierData = self.rumaClient.CarrierConfig.GetCarrierConfig(cpriPorts,flowDirection,cr_nr[1])
        tcaCarrierData.fsInfo.Bf = fs_bf
        tcaCarrierData.fsInfo.Hf = fs_hf
        tcaCarrierData.fsInfo.Addr = 1
        tcaCarrierData.gain.GainDb =Gain
        tcaCarrierData.gain.GainEnable = 1
        tcaCarrierData.enabled = 1
        self.rumaClient.CarrierConfig.SetCarrierConfig(cpriPorts,flowDirection,tcaCarrierData)
        return(cr_nr)

    def RX_add_carrier(self,cpriPorts='1A',axc_cont=0,carrier_id=1,tech='LTE',freq=15360 ,fs_hf=149,fs_bf=216,fs_adr=1,syncMode1='FSINFO'):
        flowDirection = CpriFlowDirection.RX
        if freq==960:
            cr_sr = SampleFrequency.Frequency_0_96
        elif freq==3840:
            cr_sr = SampleFrequency.Frequency_3_84
        elif freq==7680:
            cr_sr = SampleFrequency.Frequency_7_68
        elif freq==15360:
            cr_sr = SampleFrequency.Frequency_15_36
        elif freq == 23040:
            cr_sr = SampleFrequency.Frequency_23_04
        elif freq==30720:
            cr_sr = SampleFrequency.Frequency_30_72
        else:
            print('No such sample rate',freq)

        if tech=='GSM':
            cr_rat = Technology.GSM
        elif tech=='WCDMA_5_BIT':
            cr_rat =Technology.WCDMA_5_BIT
        elif tech=='LTE':
            cr_rat = Technology.LTE
        elif tech=='CDMA':
            cr_rat = Technology.CDMA
        elif tech=='WCDMA_7_BIT':
            cr_rat = Technology.WCDMA_7_BIT
        else:
            print('No such Technology',tech)
        dummy1 = int(1);dummy2 = ''
        print(cpriPorts,flowDirection,carrier_id,axc_cont,cr_sr,cr_rat)
        cr_nr=self.rumaClient.CarrierConfig.AddCarrier(cpriPorts,flowDirection, carrier_id, axc_cont, cr_sr, cr_rat,dummy1,dummy2)
        tcaCarrierData = self.rumaClient.CarrierConfig.GetCarrierConfig(cpriPorts,flowDirection,cr_nr[1])
        tcaCarrierData.fsInfo.Bf = fs_bf
        tcaCarrierData.fsInfo.Hf = fs_hf
        tcaCarrierData.fsInfo.BfOffset = 0
        if syncMode1=='FSINFO':
            tcaCarrierData.syncMode = SyncMode.FSINFO
        elif syncMode1=='CUSTOM':
            tcaCarrierData.syncMode =SyncMode.CUSTOM
        tcaCarrierData.enabled = 1
        self.rumaClient.CarrierConfig.SetCarrierConfig(cpriPorts,flowDirection,tcaCarrierData);
        return(cr_nr);

    def DeleteAllCarriers(self,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        self.rumaClient.CarrierConfig.DeleteAllCarriers(cpriPorts, flowDirection)

    def DeleteCarrier(self,carrierIndex,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        for i in carrierIndex:
            self.rumaClient.CarrierConfig.DeleteCarrier(cpriPorts, flowDirection, carrierIndex(i))

    def GetAllCarriers(self,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        NoCarrier=self.rumaClient.CarrierConfig.GetAllCarriers(cpriPorts,flowDirection)
        return NoCarrier

    def GetCarrierConfig(self,carrierIndex,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        CarrierConfigs=self.rumaClient.CarrierConfig.GetCarrierConfig(cpriPorts,flowDirection,carrierIndex)
        return CarrierConfigs

    def SetCarrierGain(self,gain,carrier,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        tcaCarrierData = self.rumaClient.CarrierConfig.GetCarrierConfig(cpriPorts,flowDirection,carrier)
        tcaCarrierData.gain.GainDb =gain
        tcaCarrierData.gain.GainEnable = 1
        tcaCarrierData.enabled = 1
        self.rumaClient.CarrierConfig.SetCarrierConfig(cpriPorts,flowDirection,tcaCarrierData)

    def SetCarrierConfig(self,carrierData,cpriPorts='1A',flowDirection='TX'):
        flowDirection=self.GetFlowDirection(flowDirection)
        self.rumaClient.CarrierConfig.SetCarrierConfig(cpriPorts,flowDirection,carrierData)

    def GetFsInfo(self,carrierIndex,cpriPorts='1A'):
        crConfig = self.GetCarrierConfig(carrierIndex,cpriPorts,'RX')
        ret = self.rumaClient.CarrierConfig.CpriGetFsInfo_RX(cpriPorts,carrierIndex)
        return(ret)
        # FsInfo.Addr = ret.Addr;
        # FsInfo.Bf = ret.Bf;
        # FsInfo.BfOffset = ret.BfOffset;
        # FsInfo.Hf = ret.Hf;
        #self.rumaClient.CarrierConfig.DeleteAllCarriers(cpriPorts, flowDirection)

    def StartPlayBack(self,cpriPorts='1A'):
        flowDataTypes=[]
        flowDataTypes.append(self.TransFlowDataType('IQ'))
        flowDataTypes.append(self.TransFlowDataType('AXC'))
        self.rumaClient.CpriDataFlow.StartPlayBack(cpriPorts,flowDataTypes)

    def StopPlayBack(self,cpriPorts='1A'):
        flowDataTypes=[]
        flowDataTypes.append(self.TransFlowDataType('IQ'))
        flowDataTypes.append(self.TransFlowDataType('AXC'))
        self.rumaClient.CpriDataFlow.StopPlayBack(cpriPorts,flowDataTypes)

    #for RX
    def StartCapture(self,flowDataType,cpriPorts='1A'):
        flowDataType = self.TransFlowDataType(flowDataType)
        self.rumaClient.CpriDataFlow.StartCapture(cpriPorts,flowDataType)
    #for RX
    def StopCapture(self,flowDataType,cpriPorts='1A'):
        flowDataType = self.TransFlowDataType(flowDataType)
        self.rumaClient.CpriDataFlow.StopCapture(cpriPorts,flowDataType)
        return(0)


    def IQFileAdd(self,fileName,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.IQFileAdd(cpriPorts,fileName)
        return(0)

    def IQFileClearAll(self):
        self.rumaClient.CpriDataFlow.IQFileClearAll()
        return(0)

    def IQFileSetCurrentByName(self,fileName,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.IQFileSetCurrentByName(cpriPorts,fileName)
        return(0)

    def CpcSetAxcMode(self,axcMode,cpriPorts='1A'):
        #  TxAxcMode values : NO_AXC, AUTO_AXC, CPC_FILES(mostly used), and CPC_MERGE
        if axcMode=='NO_AXC':
            axcMode = TxAxcMode.NO_AXC
        elif axcMode=='AUTO_AXC':
            axcMode = TxAxcMode.AUTO_AXC
        elif axcMode=='CPC_FILES':
            axcMode = TxAxcMode.CPC_FILES
        elif axcMode=='CPC_MERGE':
            axcMode = TxAxcMode.CPC_MERGE
        else:
            print('Error! no such axcMode')
        self.rumaClient.CpriDataFlow.CpcSetAxcMode(cpriPorts,axcMode)
        return(0)

    def CpcFileAdd(self,fileName,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFileAdd(cpriPorts,fileName)
        return(0)

    def CpcFileSetCurrent(self,fileName,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFileSetCurrent(cpriPorts,fileName)
        return(0)
    def CpcFileSetLoopLength(self,fileName,loopLength,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFileSetLoopLength(cpriPorts,fileName,loopLength)
        return(0)
    def CpcFileSetCurrentWithLoopLength(self,fileName,loopLength,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFileSetCurrentWithLoopLength(cpriPorts,fileName,loopLength)
        return(0)
    def CpcFilesClearAll(self,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFilesClearAll(cpriPorts)
        return(0)
    def CpcFileSetLoopLengthFromIQFile(self,cpcFileName,iqFileName,cpriPorts='1A'):
        self.rumaClient.CpriDataFlow.CpcFileSetLoopLengthFromIQFile(cpriPorts,cpcFileName,iqFileName)
        return(0)

    def SetFlowDataMode(self,flowDirection,flowDataType,flowDataMode,cpriPorts='1A'):
        flowDirection = self.TransFlowDirection(flowDirection)
        flowDataType = self.TransFlowDataType(flowDataType)
        flowDataMode = self.TransFlowDataMode(flowDataMode)
        self.rumaClient.CpriDataFlow.SetFlowDataMode(cpriPorts,flowDirection,flowDataType,flowDataMode)

    def SetStartStopCondition(self,cpriPorts,flowDirection,flowDataType,startCondition,startCondParam,stopCondition,stopCondParam):
        if startCondition=='NONE':
            startCondition = FlowStartCondition.NONE
        elif startCondition=='TRIG_IN':
            startCondition = FlowStartCondition.TRIG_IN
        elif startCondition=='CPRI_TIME':
            startCondition = FlowStartCondition.CPRI_TIME
        elif startCondition=='FIRST_NON_IDLE':
            startCondition = FlowStartCondition.FIRST_NON_IDLE
        elif startCondition=='FSINFO':
            startCondition = FlowStartCondition.FSINFO
        elif startCondition=='FRAME_PRE_START':
            startCondition = FlowStartCondition.FRAME_PRE_START
        elif startCondition=='RADIO_FRAME':
            startCondition = FlowStartCondition.RADIO_FRAME

        if stopCondition=='NEVER':
            stopCondition = FlowStopCondition.NEVER
        elif stopCondition=='FLOW_STOP_COND_TRIG_IN':
            stopCondition = FlowStopCondition.FLOW_STOP_COND_TRIG_IN
        elif stopCondition=='FLOW_STOP_COND_CPRI_TIME':
            stopCondition = FlowStopCondition.FLOW_STOP_COND_CPRI_TIME
        elif stopCondition=='CPRI_TIME_LENGTH':
            stopCondition = FlowStopCondition.CPRI_TIME_LENGTH
        arrayStartCondParam=startCondParam
        # arrayStartCondParam(1) = startCondParam(1); % BF | Carrier Nr
        #  arrayStartCondParam(2) = startCondParam(2); % HF
        #  arrayStartCondParam(3) = startCondParam(3); % BFN
        #  arrayStartCondParam(4) = startCondParam(4); % BFN Offset
        # % stopConditionParameters
        # % Type: array<System..::..UInt16>[]()[][]
        # % Parameters that are specific for every stop condition. Some of the stop conditions are parameterless
        # % CpriLength: 0 = Basic Frame(BF)
        # %             1 = Hyper Frame(HF)
        # %             2 = Radio Frame Number(BFN)
        # %             3 = Offset for Radio Frame Number(BFN OFFSET)
        arrayStopCondParam=stopCondParam
        #arrayStopCondParam = NET.createArray('System.UInt16',4);
        # arrayStopCondParam(1) = stopCondParam(1); % BF
        # arrayStopCondParam(2) = stopCondParam(2); % HF
        # arrayStopCondParam(3) = stopCondParam(3); % BFN
        # arrayStopCondParam(4) = stopCondParam(4); % unused
        flowDirection = self.TransFlowDirection(flowDirection)
        flowDataType = self.TransFlowDataType(flowDataType)
        self.rumaClient.CpriDataFlow.SetStartStopCondition(cpriPorts,flowDirection,flowDataType,startCondition,arrayStartCondParam,stopCondition,arrayStopCondParam);


    def SetAxcContainerFormat(self,flowDirection,containerFormat,cpriPorts='1A'):
        if containerFormat =='30 Bit':
            source = AxcContainerFormat.AXC_30_BIT
        elif containerFormat == '24 Bit':
            source = AxcContainerFormat.AXC_24_BIT
        elif containerFormat == '20 Bit':
            source = AxcContainerFormat.AXC_20_BIT
        elif containerFormat == 'FSINFO_CHANGED':
            source = CpriTrigSource.FSINFO_CHANGED
        flowDirection = self.TransFlowDirection(flowDirection)
        self.rumaClient.CpriDataFlow.SetAxcContainerFormat(cpriPorts, flowDirection, containerFormat)

    #capture RX IQ
    def GetCarrierSamples(self,Sample_length=38400,HF=0,BF=0,carrierIndex=0,startCondition= 'FRAME_PRE_START',cpriDataConfig=[],cpriPorts= '1A'):
        '''
        Sample_length is the Basic Frame numbers sample to capture(3.84M)
        HF,Bf is the start position for mode 'FRAME_PRE_START', ohterwise set to [0,0,0,0]
        carrierIndex=0 set to 0 corresponding to RX_carrier setup (carrier_id=0) , but Tx use 1
        startCondition= 'FRAME_PRE_START',this mode no corruption if no RX signal
        '''
        sampPerBf = 4
        containerFormat = 30
        iqFormat = 'UL'
        #startCondition = 'FIRST_NON_IDLE'
        #startCondition = 'FSINFO'
        stopCondition = 'CPRI_TIME_LENGTH'
        dataFlowMode = 'Carrier'
        currFlowState = self.GetOneFlowState(cpriPorts='1A',flowDirection='RX',flowDataType='IQ') #get capture status
        if (currFlowState == FlowState.ACTIVE):
            self.StopCapture(FlowDataType='IQ',cpriPorts='1A')
            print('----stop-first------')
        self.SetFlowDataMode('RX', 'IQ',dataFlowMode,'1A')
        if (startCondition=='NONE') |(startCondition=='RADIO_FRAME') |(startCondition=='FIRST_NON_IDLE') | (startCondition=='TRIG_IN'):
            startCondParam=[0,0,0,0]
        #can not use this one
        elif (startCondition=='CPRI_TIME'):
            startCondParam=[0,0,0,0]
        elif (startCondition=='FSINFO'):
            startCondParam=[carrierIndex,0,0,0]
        elif (startCondition=='FRAME_PRE_START'):
            startCondParam=[HF,BF,0,0]
        #stop condition setting
        if stopCondition=='CPRI_TIME_LENGTH':
            BfLength=Sample_length
            stopCondParam=[Sample_length%256,Sample_length//256%150,Sample_length//256//150,0]
        elif (stopCondition=='NEVER'):
            stopCondParam=[0,0,0,0]
        self.SetStartStopCondition(cpriPorts, 'RX', 'IQ', startCondition, startCondParam, stopCondition, stopCondParam);
        self.StartCapture('IQ',cpriPorts)
        for i in range(100):
            currFlowState = self.GetOneFlowState(cpriPorts, 'RX', 'IQ')
            #print(i,currFlowState,FlowState.STOPPED)
            if (currFlowState == FlowState.STOPPED):
                break
            else:
                time.sleep(0.005)   # wait for 5ms each time.
        currFlowState = self.GetOneFlowState(cpriPorts, 'RX', 'IQ')
        if currFlowState != FlowState.STOPPED:
            print('Sampling data time out for 5 seconds, too long???')
        #carrierData = self.GetCarrierConfig(carrierIndex,cpriPorts, 'RX', )
        #print(carrierData,'carrier data')
        m_data = self.rumaClient.CpriDataFlow.GetCarrierSamples(cpriPorts, carrierIndex, 0, BfLength, True, WcdmaSampleOption.sample_1)
        #m_data = numpy.vectorize(complex)(list(m_data)[0::2],list(m_data)[1::2])
        m_data = list(m_data)
        print('finished capture')
        return m_data

    ##this one is much slower due to for circile
    # def extract_lte(self, iq_data):
    #     iq_data = numpy.vectorize(complex)(list(iq_data)[0::2],list(iq_data)[1::2])
    #     for i, sample in numpy.ndenumerate(iq_data):
    #         # Mantissa is 12 bits [11:0]s
    #         mantissa_i = sample.real.astype(numpy.int64) & 0x64fff
    #         mantissa_q = sample.imag.astype(numpy.int64) & 0x64fff
    #         #The exponent is 4 bits [19:16] and common for both I and Q. TODO: Check this bit-range
    #         exponent = (sample.real.astype(numpy.int64) & 0x64f0000) >> 16
    #         if exponent != (sample.imag.astype(numpy.int64) & 0x64f0000) >> 16:
    #             raise Exception("The exponent shall be common for both I and Q")
    #         mantissa_i = -(mantissa_i & 0x64800) + (mantissa_i & 0x647ff)
    #         mantissa_q = -(mantissa_q & 0x64800) + (mantissa_q & 0x647ff)
    #         iq_data[i] = mantissa_i*2**exponent + 1j*mantissa_q*2**exponent
    #     return iq_data

    def extract_lte(self, iq_data):
        #default IQ 12 bit and 4bit expenent, incase 10bitIQ , need and 0x1ff and ..........
        iq_data_integer=(numpy.bitwise_and(iq_data,0X7ff)-numpy.bitwise_and(iq_data,0X800))*(2**(numpy.right_shift(numpy.bitwise_and(iq_data,0XF0000),16)))
        iq_data_complex = numpy.vectorize(complex)(iq_data_integer[0::2],iq_data_integer[1::2])
        return iq_data_complex

    def extract_lte_10bit(self, iq_data):
        #default IQ 12 bit and 4bit expenent, incase 10bitIQ , need and 0x1ff and ..........
        iq_data_integer=(numpy.bitwise_and(iq_data,0X1ff)-numpy.bitwise_and(iq_data,0X200))*(2**(numpy.right_shift(numpy.bitwise_and(iq_data,0XF0000),16)))
        iq_data_complex = numpy.vectorize(complex)(iq_data_integer[0::2],iq_data_integer[1::2])
        return iq_data_complex

    def extract_lte_9bit(self, iq_data):
        #default IQ 12 bit and 4bit expenent, incase 10bitIQ , need and 0x1ff and ..........
        iq_data_integer=(numpy.bitwise_and(iq_data,0Xff)-numpy.bitwise_and(iq_data,0X100))*(2**(numpy.right_shift(numpy.bitwise_and(iq_data,0XF0000),16)))
        iq_data_complex = numpy.vectorize(complex)(iq_data_integer[0::2],iq_data_integer[1::2])
        return iq_data_complex


    def SetCpriTriggerSource(self,triggerPort='1',source='TXK285',cpriPorts='1A'):
        print("triggerPort=",triggerPort,'CpriTrigSource=',source,'cpriPorts=',cpriPorts)
        if source =='CPC':
            source = CpriTrigSource.CPC
        elif source == 'CTT':
            source = CpriTrigSource.CTT
        elif source == 'DYNAMIC_GAIN':
            source = CpriTrigSource.DYNAMIC_GAIN
        elif source == 'FSINFO_CHANGED':
            source = CpriTrigSource.FSINFO_CHANGED
        elif source == 'RXK285':
            source = CpriTrigSource.RXK285
        elif source == 'TXK285':
            source = CpriTrigSource.TXK285

        self.rumaClient.TriggerConfig.SetCpriTriggerSource(triggerPort,cpriPorts,source)

    def EnableDebugPort(self):
        #no used
        self.rumaClient.DebugPortConfig.EnableRuFpgaUart(True)

    def DisableDebugPort(self):
        #no used
        self.rumaClient.DebugPortConfig.EnableRuFpgaUart(False)

    def SetupTriggerAdjustment(self,triggerPort='1',pulseOffset=0,pulseWidth=255,finePhaseAdjust=0):
        self.rumaClient.TriggerConfig.SetupTriggerAdjustment(triggerPort,pulseOffset,pulseWidth,finePhaseAdjust)

    def CreateCOMPort(self,comPort,baudRate,cpriPorts='1A'):
        if cpriPorts =='1A':
            portId = self.rumaClient.OoM.Tpf.CreateCOMPort(0,2,comPort,True,baudRate,1)
        elif cpriPorts=='1B':
            portId = self.rumaClient.OoM.Tpf.CreateCOMPort(0,2,comPort,True,baudRate,1)

    def DestroyCOMPort(self,portId):
        self.rumaClient.OoM.Tpf.DestroyCOMPort(portId)
    def TpfClearAll(self):
        self.rumaClient.OoM.Tpf.ClearAll( )
    def TpfExit(self):
        self.rumaClient.OoM.Tpf.Exit( )
    def TpfInit(self):
        self.rumaClient.OoM.Tpf.Init( )

    def SetMemoryMode(self,mode='CPRI'):
        if mode=='CPRI':
            self.rumaClient.HardwareControl.HardwareControlSetMemoryMode(HardwareMemoryMode.CPRI)
        elif mode=='GAMMA':
            self.rumaClient.HardwareControl.HardwareControlSetMemoryMode(HardwareMemoryMode.GAMMA)
