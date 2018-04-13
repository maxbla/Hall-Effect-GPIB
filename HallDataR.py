#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import visa
import datetime
import time
import os.path
import dateutil.parser

class HallDataR:
    """
    Records and stores data for the hall effect experiment
    """
    time_constants = [10e-6,30e-6,100e-6,300e-6,
                      1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,
                      1,3,10,30,100,300,
                      1e3,3e3,10e3,30e3]
    sensitivities = [2e-9,5e-9,10e-9,20e-9,50e-9,100e-9,200e-9,500e-9,
                   1e-6,2e-6,5e-6,10e-6,20e-6,50e-6,100e-6,200e-6,500e-6,
                   1e-3,2e-3,5e-3,10e-3,20e-3,50e-3,100e-3,200e-3,500e-3,
                   1.0]


    def _open_gpib_num(self, address, gpib=0):
        """
        Helper method to open a gpib device at a specified address
        
        :param address: the integer address of the requested gpib device
        :param gpib: the address of the GPIB device
        :returns: a GPIBInstrument object for the instrument at passed address 
        """
        _addr = int(address)
        _gpib = int(gpib)
        return self.rm.open_resource("GPIB" 
                                     + repr(_gpib) 
                                     + "::" 
                                     + repr(_addr) 
                                     + "::INSTR")
    
    def __init__(self, lockin1_addr=1, lockin2_addr=2, lockin3_addr=9,
                 dmm_addr=16, mag_ctrl_addr=22):
        """
        Initalized this object by initalizing variables and performing setup on
        instruments
        
        :param lockin1_addr: the integer address of the first lockin instrument
        :param lockin2_addr: the integer address of the second lockin instrument
        :param lockin3_addr: the integer address of the third lockin instrument
        :param dmm_addr: the integer address of the digital multimeter
        :param mag_ctrl_addr: the integer address of the magnet controller
        """
        self.rm = visa.ResourceManager()
        self.lockin1 = self._open_gpib_num(lockin1_addr)
        self.lockin2 = self._open_gpib_num(lockin2_addr)
        self.lockin3 = self._open_gpib_num(lockin3_addr)
        self.dmm = self._open_gpib_num(dmm_addr)
        self.mag_ctrl = self._open_gpib_num(mag_ctrl_addr)
        self.lockins = [self.lockin1, self.lockin2, self.lockin3]
        self.times = []  # time that sample i was taken at
        self.diodevs = []  # temperature sensing diode voltages
        self.currs = []  # currents through the magnet
        self.fields = [] # magnetic field in tesla (== coil constant * currs)
        self.ef_vs = []
        self.ef_os = []
        self.bf_vs = []
        self.bf_os = []
        self.ad_vs = []
        self.ad_os = []
        self.freqs = []  # list of frequencies measured
        self.data = [self.diodevs, self.currs, self.fields, self.ef_vs,
        self.ef_os, self.bf_vs, self.bf_os, self.ad_vs, self.ad_os, self.freqs]
        
    def __str__(self):
        """
        A string representation of this object. Contains measurement data.
        
        :returns: a string representation of this object
        """
        return ("Times: " + str(self.times) + '\n' 
                + "Diode Voltages: " + str(self.diodevs) + '\n'
                + "Magnet Currents: " + str(self.currs) + '\n'
                + "Magnetic Fields: " + str(self.fields) + '\n'
                + "EF Voltage R: " + str(self.ef_vs) + '\n'
                + "EF Voltage thetas: " + str(self.ef_os) + '\n'
                + "BF Voltage R: " + str(self.bf_vs) + '\n'
                + "BF Voltage thetas: " + str(self.bf_os) + '\n'
                + "AD Voltage R: " + str(self.ad_vs) + '\n'
                + "AD Voltage thetas: " + str(self.ad_os) + '\n'
                + "Frequencies: " + str(self.freqs) + '\n')
                
    def write_line_to_csv(self, filename, i):
        """
        Appends the i-th measurement to a csv file
        
        :param filename: the name of the csv file to append to
        """
        with open(filename, "a") as csv:
            csv.write(self.times[i].isoformat())
            csv.write(',')
            for datum in self.data:
                csv.write(str(datum))
                csv.write(',')
            csv.write('\n')

        
    def export_to_csv(self, filename):
        """
        Appends every measurement to a csv file
        
        :param filename: the name of the csv file to append
        """
        with open(filename, "a") as csv:
            for i in range(len(self.times)):
                self.write_line_to_csv(filename, i)
        
    def import_from_csv(self, filename):
        """
        Reads csv file, putting all data in approiate values in this class
        
        :param filename: the name of the csv file from which to read
        """
        self.times.clear()
        for datum in data:
            datum.clear()
        with open(filename, 'r') as csv:
            for line in csv:
                data = line.split(',')
                #if csv has ",," this removes empty string
                new_data = [value for value in data if value != '']
                timestamp = dateutil.parser.parse(new_data[0])
                self.times.append(timestamp)
                for i,datum in enumerate(data):
                    self.datum.append(float(new_data[i]))

    def multi_measure(self, fields, filename):
        """
        Change the field of the magnet to specified values, wait, measure and
        add the data to a csv
        
        :param fields: iterable of field strengths of the magnet
        :param filename: the filename of the csv file to append to
        """
        starttime = time.time()
        for field in fields:
            self.change_field(field)
            for _ in range(5):
                time.sleep(3*self.time_constants[self.time_constant])
                index = self.measure()
                self.write_line_to_csv(filename, index)
        self.mag_ctrl.write("CONF:CURR:PROG " + str(0))

    def measure(self):
        """
        Take measurements from all the instruments and record to memory
        
        :returns: the index of the measurement just recorded
        """
        self.times.append(datetime.datetime.now())
        self.diodevs.append(self.measure_diode())
        self.currs.append(self.measure_current())
        self.fields.append(self.measure_field())
        self.bf_vs.append(self.measure_r_lockin(0))
        self.bf_os.append(self.measure_o_lockin(0))
        self.ef_vs.append(self.measure_r_lockin(1))
        self.ef_vs.append(self.measure_o_lockin(1))
        self.ad_vs.append(self.measure_r_lockin(2))
        self.ad_vs.append(self.measure_o_lockin(2))
        self.freqs.append(self.measure_frequency())
        return len(self.times)-1
        
    def setup(self, freq=517.94746792, time_constant=7):
        """
        Initalize instruments by sending configuration strings over GPIB
        """
        self.freq = freq
        #100 ms time constant (machine has discrete time constants)
        self.time_constant = time_constant
        self.coil_constant = .06914

        for lockin in self.lockins:
            lockin.write("*RST")  # Reset all settings
            lockin.write("OUTX 1")  # Set to output to GPIB
            lockin.write("ISRC 1")  # Set to A-B mode
            lockin.write("IGND 1")  # Set Ground to Chassis Ground
            lockin.write("ICPL 1")  # Set input coupling to DC (ac seems broken)
            # lockin.write("DDEF 1 1 0")  # Doesn't work
            # lockin.write("DDEF 2 1 0")  # Doesn't work
            lockin.write("OFLT " + str(self.time_constant))
        #lockin1 generates function (internal refrence source)
        self.lockin1.write("FMOD 1")
        #lockin2 recieves signal from lockin1 (external reference source)
        self.lockin2.write("FMOD 0")
        self.lockin3.write("FMOD 2")
        #set lockin1 frequency to freq Hz
        self.lockin1.write("FREQ " + str(self.freq))
        #set lockin1 amplitude to 1V
        self.lockin1.write("SLVL 1.0")
        #set lockin1 sensitivity to 1V
        self.lockin1.write("SENS 26")
        
        self.dmm.write("*RST")
        self.dmm.write("CONF:VOLT:AC")

        self.mag_ctrl.write("CONF:CURR:MAX 72")
        self.mag_ctrl.write("CONF:COIL "+ self.coil_constant)
        self.mag_ctrl.write("CONF:FIELD:UNITS:1")
        self.mag_ctrl.write("CONF:PS 1")
        self.mag_ctrl.write("CONF:PS:CURR 53")
        self.mag_ctrl.write("PS 1")
        self.mag_ctrl.write("CONF:STAB 50")
    
    def id_instruments(self):  # remove this function?
        """
        Print the response to *IDN? request for each instrument
        """
        print("Lock-in 1:", self.lockin1.query("*IDN?"))
        print("Lock-in 2:", self.lockin2.query("*IDN?"))
        print("Digital Multimeter:", self.dmm.query("*IDN?"))
        #print("Temperature Controller:", self.dmm.query("*IDN?"))
        
    def set_current_limit(self, current):
        """
        Sets the current limit of the magnet controller. This is used as a
        safety mechanism to not overload the magnet
        
        :param current: the maximum current to send to the magnet in amperes
        """
        self.current = current
        mag_ctrl.write('CONF:CURR:PROG ' + current)

    def change_current(self, amps):
        """
        Sets the current through the magnet. Blocks until desired current is
        achieved
        
        :param amps: the desired amperage through the magnet
        """
        self.mag_ctrl.write("CONF:CURR:PROG " + str(amps))
        self.mag_ctrl.write('RAMP')
        while (float(self.mag_ctrl.query("CURR:MAG?")) > 1.1*amps
               or float(self.mag_ctrl.query("CURR:MAG?")) < .9*amps):
            time.sleep(.1)
        time.sleep(.5)
        self.mag_ctrl.write("PAUSE")
        
    def change_field(self, field):
        """
        Sets the field strength of the magnet. Blocks until desired field 
        strength is achieved
        
        :param field: the desired magnetic field of the magnet in tesla
        """
        self.mag_ctrl.write("CONF:FIELD:PROG " + str(field))
        self.mag_ctrl.write('RAMP')
        while (float(self.mag_ctrl.query("FIELD:MAG?")) > 1.1*field
               or float(self.mag_ctrl.query("FIELD:MAG?")) < .9*field):
            pass
        time.sleep(.5)
        self.mag_ctrl.write("PAUSE")

    def set_freq(self, freq):
        """
        Sets the frequency of lockin1 (the lockin that generates the signal)
        
        :param freq: the desired frequenct of lockin 1
        """
        self.lockin1.write("FREQ " + str(freq))
    
    def measure_diode(self):
        """
        Gets the voltage across the diode from the digital multimeter
        
        :returns: the voltage across the diode
        """
        return float(self.dmm.query("READ?"))

    def measure_r_lockin(self, lockin_num):
        """
        Measure the R value of a lockin amplifier
        
        :param lockin_num: the number of the lockin amplifier to measure
        :returns: R (as in ploar coordinates) of lockin number lockin_num
        """
        return float(self.lockins[lockin_num].query("OUTP? 3"))

    def measure_o_lockin(self, lockin_num):
        """
        Measure the theta value of a lockin amplifier
        
        :param lockin_num: the number of the lockin amplifier to measure
        :returns: theta (as in ploar coordinates) of lockin number lockin_num
        """
        return float(self.lockins[lockin_num].query("OUTP? 4"))

    def measure_frequency(self):
        """
        Measure the frequency of lockin1
        
        :returns: frequency in hertz of lockin1
        """
        return float(self.lockin1.query("FREQ?"))

    def measure_field(self):
        """
        Measure the field strength of the magnet in tesla (T)
        
        :returns: the field strength of the magnet
        """
        return float(self.mag_ctrl.query("FIELD:MAG?"))

    def measure_current(self):
        """
        Measure the current through the magnet in amps
        
        :returns: the current through the magnet in amperes
        """
        return float(self.mag_ctrl.query("CURR:MAG?"))
