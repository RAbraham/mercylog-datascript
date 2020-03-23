// Transcrypt'ed from Python, 2019-10-27 22:19:39
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __proxy__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, print, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
var __name__ = '__main__';
export var DataScriptDemo =  __class__ ('DataScriptDemo', [object], {
	__module__: __name__,
	get get_result () {return __get__ (this, function (self) {
		var db = datascript.empty_db ();
		var db1 = datascript.db_with (db, [[':db/add', 1, 'name', 'Ivan'], [':db/add', 1, 'age', 17]]);
		var db2 = datascript.db_with (db1, [dict ({':db/id': 2, 'name': 'Igor', 'age': 35})]);
		var q = '[:find ?n ?a :where [?e "name" ?n] [?e "age" ?a]]';
		var result = datascript.q (q, db2);
		document.getElementById ('greet').innerHTML = str (result);
	});}
});
export var datascript_demo = DataScriptDemo ();

//# sourceMappingURL=datascript_demo.map