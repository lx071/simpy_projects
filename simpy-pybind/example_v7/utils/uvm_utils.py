import simpy
from .tlm_utils import *

# uvm_void => uvm_object 
# uvm_object => uvm_transaction => uvm_sequence_item => uvm_sequence_base => uvm_sequence 
# uvm_object => uvm_transaction => uvm_sequence_item => uvm_tlm_generic_payload 
# uvm_object => uvm_report_object => uvm_component => uvm_sequencer_base => uvm_sequencer_param_base => uvm_sequencer 
# uvm_object => uvm_report_object => uvm_component => uvm_driver 


# 对应 uvm_pkg 中的 uvm_sequence_item 类
class uvm_sequence_item:
    # The constructor method for uvm_sequence_item. 
    def __init__(self, name = "uvm_sequence_item"):
        self.name = name
        self.m_sequence_id = -1
        self.m_use_sequence_info = 0
        self.m_depth = -1
        self.m_sequencer = None
        self.m_parent_sequence = None


    def get_type_name(self):
        return "uvm_sequence_item"
     

    # Function- set_sequence_id
    def set_sequence_id(self, id):
        self.m_sequence_id = id
    

    # Function: get_sequence_id
    # private
    def get_sequence_id(self):
        return (self.m_sequence_id)


    # Function: set_item_context
    # Set the sequence and sequencer execution context for a sequence item
    def set_item_context(self, parent_seq, sequencer = None):
        self.set_use_sequence_info(1)
        if parent_seq != None:
            self.set_parent_sequence(parent_seq)
        if sequencer == None and self.m_parent_sequence != None:
            sequencer = self.m_parent_sequence.get_sequencer()
        self.set_sequencer(sequencer)
        if self.m_parent_sequence != None:
            self.set_depth(self.m_parent_sequence.get_depth() + 1)
        # reseed()      
    

    # Function: set_use_sequence_info
    def set_use_sequence_info(self, value):
        self.m_use_sequence_info = value
    

    # Function: get_use_sequence_info
    # These methods are used to set and get the status of the use_sequence_info
    # bit. Use_sequence_info controls whether the sequence information
    # (sequencer, parent_sequence, sequence_id, etc.) is printed, copied, or
    # recorded. When use_sequence_info is the default value of 0, then the
    # sequence information is not used. When use_sequence_info is set to 1,
    # the sequence information will be used in printing and copying.
    def get_use_sequence_info(self):
        return (self.m_use_sequence_info)
    

    # Function: set_id_info
    # Copies the sequence_id and transaction_id from the referenced item into
    # the calling item.  This routine should always be used by drivers to
    # initialize responses for future compatibility.
    def set_id_info(self, item):
        if item == None:
            # uvm_report_fatal(get_full_name(), "set_id_info called with null parameter", UVM_NONE)
            print("ERROR: set_id_info called with null parameter")
            raise ResponseError("set_id_info called with null parameter")
        # self.set_transaction_id(item.get_transaction_id())
        self.set_sequence_id(item.get_sequence_id())
    

    # Function: set_sequencer
    # Sets the default sequencer for the sequence to sequencer.  It will take
    # effect immediately, so it should not be called while the sequence is
    # actively communicating with the sequencer.
    def set_sequencer(self, sequencer):
        self.m_sequencer = sequencer
        # self.m_set_p_sequencer()
    

    # Function: get_sequencer
    # Returns a reference to the default sequencer used by this sequence.
    def get_sequencer(self):
        return self.m_sequencer
    

    # Function: set_parent_sequence
    # Sets the parent sequence of this sequence_item.  This is used to identify
    # the source sequence of a sequence_item.
    def set_parent_sequence(self, parent):
        self.m_parent_sequence = parent
    

    # Function: get_parent_sequence
    # Returns a reference to the parent sequence of any sequence on which this
    # method was called. If this is a parent sequence, the method returns null.
    def get_parent_sequence(self):
        return (self.m_parent_sequence)
     

    # Function: set_depth
    # The depth of any sequence is calculated automatically.  However, the user
    # may use  set_depth to specify the depth of a particular sequence. This
    # method will override the automatically calculated depth, even if it is
    # incorrect.  
    def set_depth(self, value):
        self.m_depth = value
    

    # Function: get_depth
    # Returns the depth of a sequence from it's parent.  A  parent sequence will
    # have a depth of 1, it's child will have a depth  of 2, and it's grandchild
    # will have a depth of 3.
    def get_depth(self):
        # If depth has been set or calculated, then use that
        if self.m_depth != -1:
            return (self.m_depth)

        # Calculate the depth, store it, and return the value
        if self.m_parent_sequence == None:
            self.m_depth = 1
        else:
            self.m_depth = self.m_parent_sequence.get_depth() + 1

        return (self.m_depth)


# 通用负载, 对应 SystemC 的 tlm_generic_payload 类和 uvm_pkg 中的 uvm_tlm_generic_payload 类
class uvm_tlm_generic_payload(uvm_sequence_item):
    # Generic Payload attributes:
    # m_command, m_address, m_data, m_length, m_response_status, m_byte_enable, m_byte_enable_length, m_streaming_width
    def __init__(self) -> None:        
        self.m_address = None           # sc_dt::uint64
        self.m_command = None           # tlm_command
        self.m_data = None              # unsigned char*
        self.m_length = 0               # unsigned int
        self.m_response_status = None   # tlm_response_status
        self.m_dmi = False              # bool
        self.m_byte_enable = None       # unsigned char*
        self.m_byte_enable_length = 0   # unsigned int
        self.m_streaming_width = 0      # unsigned int
        self.m_gp_option = None         # tlm_gp_option

    '''
    //----------------
    // API (including setters & getters)
    //---------------
    '''
    # Command related method
    def is_read(self): 
        return self.m_command == tlm_command.TLM_READ_COMMAND
    def set_read(self):
        self.m_command = tlm_command.TLM_READ_COMMAND
    def is_write(self):
        return self.m_command == tlm_command.TLM_WRITE_COMMAND
    def set_write(self):
        self.m_command = tlm_command.TLM_WRITE_COMMAND
    def get_command(self):
        return self.m_command
    def set_command(self, command):
        self.m_command = command

    # Address related methods
    def get_address(self):
        return self.m_address
    def set_address(self, address):
        self.m_address = address

    # Data related methods
    def get_data_ptr(self):
        return self.m_data
    def set_data_ptr(self, data):
        self.m_data = data

    # Transaction length (in bytes) related methods
    def get_data_length(self):
        return self.m_length
    def set_data_length(self, length):
        self.m_length = length

    # Response status related methods
    def is_response_ok(self):
        return self.m_response_status > 0
    def is_response_error(self) -> bool:
        return self.m_response_status <= 0
    def get_response_status(self):
        return self.m_response_status
    def set_response_status(self, response_status, socket):
        self.m_response_status = response_status
        # Mandatory initial value
        if self.m_response_status == tlm_response_status.TLM_INCOMPLETE_RESPONSE:   
            socket.block_event = simpy.Event(socket.env)
        # indicate successful completion
        elif self.m_response_status == tlm_response_status.TLM_OK_RESPONSE:
            if not socket.block_event.triggered:
                socket.block_event.succeed()    # 要求传入 initiator 端的 socket
    def get_response_string(self):
        pass

    # Streaming related methods
    def get_streaming_width(self): 
        return self.m_streaming_width
    def set_streaming_width(self, streaming_width):
        self.m_streaming_width = streaming_width

    # Byte enable related methods
    def get_byte_enable_ptr(self):
        return self.m_byte_enable
    def set_byte_enable_ptr(self, byte_enable):
        self.m_byte_enable = byte_enable
    def get_byte_enable_length(self):
        return self.m_byte_enable_length
    def set_byte_enable_length(self, byte_enable_length):
        self.m_byte_enable_length = byte_enable_length

    # This is the "DMI-hint" a slave can set this to true if it
    # wants to indicate that a DMI request would be supported:
    def set_dmi_allowed(self, dmi_allowed):
        self.m_dmi = dmi_allowed
    def is_dmi_allowed(self):
        return self.m_dmi

    # Use full set of attributes in DMI/debug?
    def get_gp_option(self):
        return self.m_gp_option
    def set_gp_option(self, gp_opt):
        self.m_gp_option = gp_opt


# 对应 uvm_pkg 中的 uvm_sequence 类
class uvm_sequence(uvm_sequence_item):

    def __init__(self, env, name):
        super().__init__(name)
        self.env = env


    def start(self, sequencer, parent_sequence = None):
        self.m_sequencer = sequencer
        self.set_item_context(parent_sequence, sequencer)
        self.env.process(self.body())
        

    def create_item(self):
        trans = uvm_tlm_generic_payload()
        return trans
    

    def start_item(self, item, sequencer):
        item.set_item_context(self, sequencer)
        # self.m_sequencer.wait_for_grant(this, set_priority)
        '''a user-definable callback task that is called ~on the parent sequence~ after the sequencer has selected this sequence, and before the item is randomized.''' 
        # pre_do(1) 
        pass


    def finish_item(self, item):
        sequencer = item.get_sequencer()
        if sequencer == None:
            # uvm_report_fatal("STRITM", "sequence_item has null sequencer", UVM_NONE);
            print("FATAL:", "sequence_item has null sequencer")
            raise ResponseError("sequence_item has null sequencer")
        
        '''a user-definable callback function that is called after the sequence item has been randomized, and just before the item is sent to the driver.'''        
        # mid_do(item); 

        yield self.env.process(sequencer.send_request(self, item))
        yield self.env.process(sequencer.wait_for_item_done(self, -1))
        '''a user-definable callback function that is called after the driver has indicated that it has completed the item, using either this item_done or put methods.'''
        # post_do(item);


    def send_request(self, request, rerandomize = 0):
        if self.m_sequencer == None:
            # uvm_report_fatal("SSENDREQ", "Null m_sequencer reference", UVM_NONE);
            print("FATAL:", "Null m_sequencer reference")
            raise ResponseError("Null m_sequencer reference")
        self.m_sequencer.send_request(self, request, rerandomize)


    def wait_for_item_done(self, transaction_id = -1):
        if self.m_sequencer == None:
            # uvm_report_fatal("WAITITEMDONE", "Null m_sequencer reference", UVM_NONE);
            print("FATAL:", "Null m_sequencer reference")
            raise ResponseError("Null m_sequencer reference")
        self.m_sequencer.wait_for_item_done(self, transaction_id)


# 对应 uvm_pkg 中的 uvm_sequencer 类
class uvm_sequencer(Module):
    
    m_id = 0

    def __init__(self, env, name):
        super().__init__(env, name)
        self.sequence_item_requested = 0
        self.get_next_item_called = 0

        self.socket = Socket(self)

        self.socket.register_get_next_item(self.get_next_item)
        self.socket.register_item_done(self.item_done)

        # uvm_tlm_fifo #(REQ) m_req_fifo;
        self.store = simpy.Store(env, capacity=1)

        self.reg_sequences = []

        uvm_sequencer.m_id += 1
        self.m_sequencer_id = uvm_sequencer.m_id

        self.m_wait_for_item_sequence_id = 0
        self.m_wait_for_item_transaction_id = 0

        self.item_done_e = self.env.event()


    def get_next_item(self, trans):
        ptr = trans.get_data_ptr()

        if self.get_next_item_called == 1:
            # uvm_report_error(get_full_name(), "Get_next_item called twice without item_done or get in between", UVM_NONE);
            print("ERROR:", "Get_next_item called twice without item_done or get in between")
        
        # if not self.sequence_item_requested:
        #     m_select_sequence()

        # Set flag indicating that the item has been requested to ensure that item_done or get
        # is called between requests
        self.sequence_item_requested = 1
        self.get_next_item_called = 1
        # self.m_req_fifo.peek(t)
        
        item = yield self.store.get()
        
        ptr[0] = item.get_data_ptr()
        trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
    

    def item_done(self, item = None):
        self.sequence_item_requested = 0
        self.get_next_item_called = 0

        self.item_done_e.succeed()
        self.item_done_e = self.env.event()  
        if item != None:
            self.put_response(item)


    def send_request(self, sequence_ptr, t: uvm_tlm_generic_payload, rerandomize = 0):
        t.set_sequencer(self)
        # if self.m_req_fifo.try_put(t) != 1:
        yield self.store.put(t)
        #     # uvm_report_fatal(get_full_name(), "Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver", UVM_NONE);
        #     print("Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver")
        #     raise ResponseError("Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver")


    def put_response(self, t: uvm_tlm_generic_payload):
        sequence_ptr = self.reg_sequences[t.get_sequence_id()]
        sequence_ptr.put_response(t)


    def wait_for_item_done(self, sequence_ptr, transaction_id):
        # sequence_id = sequence_ptr.m_get_sqr_sequence_id(self.m_sequencer_id, 1)
        # self.m_wait_for_item_sequence_id = -1
        # self.m_wait_for_item_transaction_id = -1
        yield self.item_done_e
        pass


# 对应 uvm_pkg 中的 uvm_driver 类
class uvm_driver(Module):

    def __init__(self, env, name):
        super().__init__(env, name)

        # 创建 socket，与 sequencer 进行连接
        self.socket = Socket(self)
        

