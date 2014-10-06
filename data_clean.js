/*
清洗phone_record 中的数据
 */


var t = db.phone_record.findOne({$where:"this.province==this.city","province":{"$exists":true}})
a = [ ];
while ( t != null ){
	var zip_code = t.zip_code;
	a.push(zip_code)
	var p =db.phone_record.findOne({"zip_code":zip_code,"$where":"this.province!=this.city","province":{"$ne":''}});
	if (p != null){
		delete p['_id'];
		db.phone_record.update({"zip_code":zip_code},{"$set":p},{multi:true});
	}
	t = db.phone_record.findOne({$where:"this.province==this.city","province":{"$exists":true},"zip_code":{'nin':a}});
}
