import sys, os
import logging
logging.basicConfig()
##logging.basicConfig(level=logging.DEBUG)
##logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\..")))

import ctypes
import comtypes
from comtypes.hresult import *
import comtypes.client
import comtypes.errorinfo
import comtypes.server
import comtypes.server.connectionpoints
import comtypes.typeinfo

################################################################

# Create the wrapper in the comtypes.gen package, it will be named
# TestComServerLib; the name is derived from the 'library ' statement
# in the IDL file
if not hasattr(sys, "frozen"):
    # pathname of the type library file
    tlbfile = os.path.join(os.path.dirname(__file__), "TestDispServer.tlb")
    # if running as frozen app (dll or exe), the wrapper should be in
    # the library archive, so we don't need to generate it.
    comtypes.client.GetModule(tlbfile)

# Import the wrapper
from comtypes.gen import TestDispServerLib

################################################################

# Implement the CoClass.  Use the coclass from the wrapper as base
# class, and use DualDispMixin as base class which provides default
# implementations of IDispatch, IProvideClassInfo, IProvideClassInfo2
# interfaces.  ISupportErrorInfo is implemented by the COMObject base
# class.
class TestDispServer(
    TestDispServerLib.TestDispServer, # the coclass from the typelib wrapper
    comtypes.server.connectionpoints.ConnectableObjectMixin,
    ):

    # The default interface from the typelib MUST be the first
    # interface, other interfaces can follow

    _com_interfaces_ = TestDispServerLib.TestDispServer._com_interfaces_ + \
                       [comtypes.typeinfo.IProvideClassInfo2,
                        comtypes.errorinfo.ISupportErrorInfo,
                        comtypes.connectionpoints.IConnectionPointContainer,
                        ]

    # registry entries
    _reg_threading_ = "Both"
    _reg_progid_ = "TestDispServerLib.TestDispServer.1"
    _reg_novers_progid_ = "TestDispServerLib.TestDispServer"
    _reg_desc_ = "comtypes COM server sample for testing"
    _reg_clsctx_ = comtypes.CLSCTX_INPROC_SERVER | comtypes.CLSCTX_LOCAL_SERVER

    ################################
    # DTestDispServer methods

    def DTestDispServer_eval(self, this, expr, presult):
        self.Fire_Event(0, "EvalStarted", expr)
        presult[0].value = eval(expr)
        self.Fire_Event(0, "EvalCompleted", expr, presult[0].value)
        return S_OK

    def DTestDispServer_eval2(self, expr):
        self.Fire_Event(0, "EvalStarted", expr)
        result = eval(expr)
        self.Fire_Event(0, "EvalCompleted", expr, result)
        return result

    def DTestDispServer__get_id(self, this, pid):
        pid[0] = id(self)
        return S_OK

    _name = u"spam, spam, spam"

    # Implementation of the DTestDispServer::Name propget
    def DTestDispServer__get_name(self, this, pname):
        pname[0].value = self._name
        return S_OK

    # Implementation of the DTestDispServer::Name propput
    def DTestDispServer__set_name(self, this, name):
        self._name = name
        return S_OK

    # Implementation of the DTestDispServer::SetName method
    def DTestDispServer_sEtNaMe(self, name):
        self._name = name

if __name__ == "__main__":
    from comtypes.server.register import UseCommandLine
    UseCommandLine(TestDispServer)