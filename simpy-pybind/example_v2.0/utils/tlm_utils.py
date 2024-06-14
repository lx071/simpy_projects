import simpy

class ResponseError(Exception):
    pass

# 三种命令, 对应 SystemC 的 enum tlm_command
class tlm_command:
    TLM_READ_COMMAND = 0
    TLM_WRITE_COMMAND = 1
    TLM_IGNORE_COMMAND = 2

# Response status attribute (六种错误响应), 对应 SystemC 的 enum tlm_response_status
class tlm_response_status:
    TLM_OK_RESPONSE = 1
    TLM_INCOMPLETE_RESPONSE = 0
    TLM_GENERIC_ERROR_RESPONSE = -1
    TLM_ADDRESS_ERROR_RESPONSE = -2
    TLM_COMMAND_ERROR_RESPONSE = -3
    TLM_BURST_ERROR_RESPONSE = -4
    TLM_BYTE_ENABLE_ERROR_RESPONSE = -5

# 四个阶段, 对应 SystemC 的 tlm_phase 类 和 enum tlm_phase_enum
class tlm_phase:
    UNINITIALIZED_PHASE = 0
    BEGIN_REQ = 1
    END_REQ = 2
    BEGIN_RESP = 3
    END_RESP = 4
    m_ex_ph = {}

    def __init__(self, id=UNINITIALIZED_PHASE) -> None:
        self.m_id = id

    # 扩展阶段
    @staticmethod
    def DECLARE_EXTENDED_PHASE(name: str):
        tlm_phase.m_ex_ph[name] = len(tlm_phase.m_ex_ph.items()) + 5


# 三种返回值, 对应 SystemC 的 enum tlm_sync_enum
class tlm_sync_enum:
    TLM_ACCEPTED = 0
    TLM_UPDATED = 1
    TLM_COMPLETED = 2


# 对应 SystemC 的 sc_module 类
class Module:
    def __init__(self, env: simpy.Environment, name: str):
        self.env = env
        self.name = name
        pass

    # called by construction_done 
    def before_end_of_elaboration(self):
        pass
    # called by elaboration_done (does nothing by default)
    def end_of_elaboration(self):
        pass
    # called by start_simulation (does nothing by default)
    def start_of_simulation(self):
        pass
    # called by simulation_done (does nothing by default)
    def end_of_simulation(self):
        pass


# 对应 SystemC 的 simple_initiator_socket_b 类和 simple_target_socket_b 类
class Socket:
    def __init__(self, module, name: str="socket"):
        self.env = module.env
        self.name = module.name + '_{}'.format(name)
        self.other_socket = None    # 指向对面的 Socket/MultiSocket
        # 核心接口(core interfaces)
        # non-blocking transport interface
        self.nb_transport_fw_func = None
        self.nb_transport_bw_func = None
        # blocking transport interface
        self.b_transport_func = None
        # the debug transport interface
        self.transport_dbg_func = None
        # the direct memory interface (DMI)
        self.get_direct_mem_ptr_func = None
        self.invalidate_direct_mem_ptr_func = None
        self.block_event = self.env.event()

        self.get_next_item_func = None
        self.item_done_func = None

    # ===   in class simple_initiator_socket_b   ===
    # 对 socket 进行绑定(对应 SystemC 中 port 与 export 的绑定)
    # initiator.port -> target.export; target.port -> initiator.export
    def bind(self, other):
        if isinstance(other, Socket):
            assert self.other_socket is None and other.other_socket is None, "Bind Error: the socket is bound"
            self.other_socket = other
            other.other_socket = self
        elif isinstance(other, MultiSocket):
            self.other_socket = other
            other.m_sockets.append(self)
            # other.other_socket = self
            pass
        else:
            assert False, "Bind Error: the other is not a socket"
    
    
    def register_get_next_item(self, func):
        self.get_next_item_func = func
    def register_item_done(self, func):
        self.item_done_func = func
    
    def get_next_item(self, trans):
        if isinstance(self.other_socket, Socket):
            self.env.process(self.other_socket.get_next_item_func(trans))
            yield self.block_event
        else:
            assert False, "get_next_item: Invalid Type"

    def item_done(self):
        if isinstance(self.other_socket, Socket):
            self.other_socket.item_done_func()
        else:
            assert False, "item_done: Invalid Type"


    # ===   in class simple_initiator_socket_b   ===

    def register_nb_transport_bw(self, func):
        self.nb_transport_bw_func = func
    def register_invalidate_direct_mem_ptr(self, func):
        self.invalidate_direct_mem_ptr_func = func

    # ===   in class simple_target_socket_b   ===
    
    def register_nb_transport_fw(self, func):
        self.nb_transport_fw_func = func
    def register_b_transport(self, func):
        self.b_transport_func = func
    def register_transport_dbg(self, func):
        self.transport_dbg_func = func
    def register_get_direct_mem_ptr(self, func):
        self.get_direct_mem_ptr_func = func
     
   
    def nb_transport_fw(self, trans, phase, t):
        assert self.other_socket.nb_transport_fw_func is not None, f"{self.other_socket.name} nb_transport_fw_func is None"
        if isinstance(self.other_socket, Socket):
            return self.other_socket.nb_transport_fw_func(trans, phase, t)
        elif isinstance(self.other_socket, MultiSocket):
            return self.other_socket.nb_transport_fw_func(trans, phase, t, self.other_socket.m_sockets.index(self))
        else:
            assert False, "nb_transport_fw: Invalid Type"
    
    def b_transport(self, payload, delay):
        assert self.other_socket.b_transport_func is not None, "Socket is None"
        if isinstance(self.other_socket, Socket):
            self.env.process(self.other_socket.b_transport_func(payload, delay))
        elif isinstance(self.other_socket, MultiSocket):
            self.env.process(self.other_socket.b_transport_func(payload, delay, self.other_socket.m_sockets.index(self)))
        else:
            assert False, "b_transport: Invalid Type"
        yield self.block_event
        # self.block_event = simpy.Event(self.env)

    def transport_dbg(self, trans):
        if isinstance(self.other_socket, Socket):
            return self.other_socket.transport_dbg_func(trans)
        elif isinstance(self.other_socket, MultiSocket):
            return self.other_socket.transport_dbg_func(trans, self.other_socket.m_sockets.index(self))
        else:
            assert False, "transport_dbg: Invalid Type"

    def get_direct_mem_ptr(self, trans, dmi_data):
        if isinstance(self.other_socket, Socket):
            return self.other_socket.get_direct_mem_ptr_func(trans, dmi_data)
        elif isinstance(self.other_socket, MultiSocket):
            return self.other_socket.get_direct_mem_ptr_func(trans, dmi_data, self.other_socket.m_sockets.index(self))
        else:
            assert False, "get_direct_mem_ptr: Invalid Type"


    def nb_transport_bw(self, trans, phase, t):
        assert self.other_socket.nb_transport_bw_func is not None, f"{self.other_socket.name} nb_transport_bw_func is None"
        if isinstance(self.other_socket, Socket):
            return self.other_socket.nb_transport_bw_func(trans, phase, t)
        elif isinstance(self.other_socket, MultiSocket):
            return self.other_socket.nb_transport_bw_func(trans, phase, t, self.other_socket.m_sockets.index(self))
        else:
            assert False, "nb_transport_bw: Invalid Type"

    def invalidate_direct_mem_ptr(self, start_range, end_range):
        if isinstance(self.other_socket, Socket):
            self.other_socket.invalidate_direct_mem_ptr_func(start_range, end_range)
        elif isinstance(self.other_socket, MultiSocket):
            self.other_socket.invalidate_direct_mem_ptr_func(start_range, end_range, self.other_socket.m_sockets.index(self))
        else:
            assert False, "invalidate_direct_mem_ptr: Invalid Type"


# 对应 SystemC 的 multi_passthrough_initiator_socket 类 和 multi_passthrough_target_socket 类
class MultiSocket:
    def __init__(self, module, name: str="socket"):
        self.env = module.env
        self.name = module.name + "_{}".format(name)
        self.other_socket = None    # 指向对面的 MultiSocket
        self.m_sockets = []         # 存储对面的 Socket 列表
        self.nb_transport_fw_func = None
        self.nb_transport_bw_func = None
        self.b_transport_func = None
        self.transport_dbg_func = None
        self.get_direct_mem_ptr_func = None
        self.invalidate_direct_mem_ptr_func = None
        self.block_event = self.env.event()
    def bind(self, other):
        if isinstance(other, Socket):
            assert other.other_socket is None, "Bind Error: the socket is bound"
            self.m_sockets.append(other)
            other.other_socket = self
        elif isinstance(other, MultiSocket):
            self.other_socket = other
            other.other_socket = self
        else:
            assert False, "Bind Error: the other is not a socket"
    def register_b_transport(self, func):
        self.b_transport_func = func

    def register_get_direct_mem_ptr(self, func):
        self.get_direct_mem_ptr_func = func

    def register_invalidate_direct_mem_ptr(self, func):
        self.invalidate_direct_mem_ptr_func = func

    def register_transport_dbg(self, func):
        self.transport_dbg_func = func

    def register_nb_transport_bw(self, func):
        self.nb_transport_bw_func = func

    def register_nb_transport_fw(self, func):
        self.nb_transport_fw_func = func

    def b_transport(self, payload, delay, id):
        assert self.m_sockets[id].b_transport_func is not None, "Socket is None"
        self.env.process(self.m_sockets[id].b_transport_func(payload, delay))
        yield self.block_event
        # self.block_event = simpy.Event(self.env)

    def nb_transport_bw(self, trans, phase, t, id):
        assert self.m_sockets[id].nb_transport_bw_func is not None, f"{self.other_socket.name} nb_transport_bw_func is None"
        return self.m_sockets[id].nb_transport_bw_func(trans, phase, t)

    def nb_transport_fw(self, trans, phase, t, id):
        assert self.m_sockets[id].nb_transport_fw_func is not None, f"{self.other_socket.name} nb_transport_fw_func is None"
        return self.m_sockets[id].nb_transport_fw_func(trans, phase, t)

    def transport_dbg(self, trans, id):
        return self.m_sockets[id].transport_dbg_func(trans)

    def get_direct_mem_ptr(self, trans, dmi_data, id):
        return self.m_sockets[id].get_direct_mem_ptr_func(trans, dmi_data)

    def invalidate_direct_mem_ptr(self, start_range, end_range, id):
        self.m_sockets[id].invalidate_direct_mem_ptr_func(start_range, end_range)
