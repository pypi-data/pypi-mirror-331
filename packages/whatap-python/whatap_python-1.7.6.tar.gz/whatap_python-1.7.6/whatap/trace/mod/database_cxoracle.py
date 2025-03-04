from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_db_con, interceptor_db_execute, interceptor_db_close

def instrument_oracle_client(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            db_type = 'oracle'
            callback = interceptor_db_con(fn, db_type, *args, **kwargs)
            return callback
        
        return trace
    if hasattr(module, "connect"):
        module.connect = wrapper(module.connect)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback
        
        return trace
    
    if hasattr(module, "Connection") and hasattr(module.Connection, "close"):
        get_dict(module.Connection)['close'] = wrapper(
            module.Connection.close)

