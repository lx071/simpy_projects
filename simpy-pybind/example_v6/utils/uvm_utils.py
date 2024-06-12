class ResponseError(Exception):
    pass


# 对应 uvm_pkg 中的 uvm_sequence_item 类
class Sequence_Item:
    # The constructor method for uvm_sequence_item. 
    def __init__(self, name = "uvm_sequence_item"):
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


