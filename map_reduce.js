
print ("start");

var m= function(){
	emit(this.zip_code,{"province":this.province,
						"city":this.city,
						"zip_code":this.zip_code,
						"code":this.code,
						"phone":this._id
						}
		);
};

var r= function(key,values){

	return values[0];
	for(i in values){
		if( values[i].province !='州市' && values[i].province != ''){
		};
	};
};

var res = db.runCommand(

		{
			mapreduce:"phone_record",
			map: m,
			reduce: r,
			out:"phone_zip_code",
			query :{"province":{"$gt":""}},
			jsMode: true,
			//limit:100
		}

);

print ("done");
