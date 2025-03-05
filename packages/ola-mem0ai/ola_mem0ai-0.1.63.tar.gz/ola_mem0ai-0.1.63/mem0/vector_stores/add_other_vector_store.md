# mem0 向量数据库需要的基础能力

本文主要用于对比 mem0 支持的 milvus 源码部分看阿里云向量数据库是否能满足，下文中*阿里云向量检索服务*简称为*阿里云向量*

## 根据 mem0源码中的 milvus 部分代码进行参考

### init函数需求
*结论：可满足*
#### mem0 文档说明
```
Initialize the MilvusDB database.
Args:
    url (str): Full URL for Milvus/Zilliz server.
    token (str): Token/api_key for Zilliz server / for local setup defaults to None.
    collection_name (str): Name of the collection (defaults to mem0).
    embedding_model_dims (int): Dimensions of the embedding model (defaults to 1536).
    metric_type (MetricType): Metric type for similarity search (defaults to L2).
```



| mem0中的要求                  | 阿里云向量                           |
|---------------------------|---------------------------------|
| collection_name 创建        | 有（Client.create 中 name 参数）      |
| embedding_model_dims 向量维度 | 有（Client.create 中 dimension 参数） |
| metric_type 相似度指标计算方法     | 有（Client.create 中 metric 参数）    |

### create_col 函数，创建 collection
*结论：可满足*
#### mem0 文档说明
```
Create a new collection with index_type AUTOINDEX.
Args:
    collection_name (str): Name of the collection (defaults to mem0).
    vector_size (str): Dimensions of the embedding model (defaults to 1536).
    metric_type (MetricType, optional): etric type for similarity search. Defaults to MetricType.COSINE
```

| mem0 中的要求                                             | 阿里云向量                                                                        |
|-------------------------------------------------------|------------------------------------------------------------------------------|
| 数据 schema 需要设置 id（char），metadata（json），vectors（float） | 有（Client.create 中 fields_schema 参数，可以指定 field 的类型，有dict,int,float,bool这几种类型） |

**这部分注意，阿里云向量的fields_schema没有 json 格式，参考源码中其他类型的数据库可以使用 json.dumps转化为字符串**


### insert函数
*结论：可满足*
#### mem0 文档说明
```
insert vectors into a collection.

Args:
    vectors (List[List[float]]): List of vectors to insert.
    payloads (List[Dict], optional): List of payloads corresponding to vectors.
    ids (List[str], optional): List of IDs corresponding to vectors.
```
| mem0 中的要求                            | 阿里云向量                  |
|--------------------------------------|------------------------|
| 向 collection 中插入 id，vector, metadata | 有（Collection.insert()） |

**insert参数中没有 collection_name 这个是在初始化的时候指定**
**阿里云向量中vector 不是在fields_schema中定义，默认就有**

### search函数
*结论：可满足*
#### mem0 文档说明
```
Search for similar vectors.

Args:
    query (List[float]): Query vector.
    limit (int, optional): Number of results to return. Defaults to 5.
    filters (Dict, optional): Filters to apply to the search. Defaults to None.

Returns:
    list: Search results.
```

| mem0 中的要求             | 阿里云向量                          |
|-----------------------|--------------------------------|
| 根据 filters 和 limit 检索 | 有（Collection.query() 所有参数均能满足） |

metadata 中包含 user_id
milvus 的特性是 metadata 使用的是 json，在 查询的时候可以直接 filter
看了其他数据库有的不支持 json，是先查出所有的相似向量，然后将 metadata 转成 json 再次进行过滤
现在还不知道查询时 filter 快还是查询后 filter 快
所以有两个方案：
- 方案 1：若查询时 filter 比较快则建议直接将 metadata 数据做成fields_schema
- 方案 2：跟其他 metadata 不支持 json 格式的数据库一样，先查询出来再进行一次过滤

### delete
*结论：可满足*
### mem0 文档说明
```
Delete a vector by ID.

Args:
    vector_id (str): ID of the vector to delete.
```

| mem0 中的要求            | 阿里云向量                                                                 |
|----------------------|-----------------------------------------------------------------------|
| 根据 vector_id 删除某一条记忆 | 有（Collection.delete() 主键 id 是 str 类型，可以将 mem0的 vector_id变成主键 id 即可满足） |

### update
*结论：可满足*
#### mem0 文档说明
```
Update a vector and its payload.
Args:
    vector_id (str): ID of the vector to update.
    vector (List[float], optional): Updated vector.
    payload (Dict, optional): Updated payload.
```
| mem0 中的要求         | 阿里云向量                                                                 |
|-------------------|-----------------------------------------------------------------------|
| 根据 vector_id 更新向量 | 有（collection.update() 主键 id 是 str 类型，可以将 mem0的 vector_id变成主键 id 即可满足） |

### get
*结论：可满足*
#### mem0 文档说明
```
Retrieve a vector by ID.

Args:
    vector_id (str): ID of the vector to retrieve.

Returns:
    OutputData: Retrieved vector.
```

| mem0 中的要求           | 阿里云向量                                                                   |
|---------------------|-------------------------------------------------------------------------|
| 根据 vector_id 检索出来向量 | 有（collection.fetch() 主键 id 是 str 类型的数组，可以将 mem0的 vector_id变成主键 id 即可满足） |

### list_cols
*结论：可满足*
#### mem0 文档说明

```
List all collections.

Returns:
    List[str]: List of collection names.
```
| mem0 中的要求           | 阿里云向量             |
|---------------------|-------------------|
| 获取所有 collection 的名字 | 有（Client.list() ） |

### delete_col
*结论：可满足*
### mem0 文档说明
```
Delete a collection.
```
| mem0 中的要求                       | 阿里云向量                                             |
|---------------------------------|---------------------------------------------------|
| 根据 collection_name删除 collection | 有（Client.delete(name: str) -> DashVectorResponse） |

### col_info
*结论：可满足*
#### mem0 文档说明
```
Get information about a collection.

Returns:
    Dict[str, Any]: Collection information.
```

| mem0 中的要求              | 阿里云向量                                               |
|------------------------|-----------------------------------------------------|
| 根据 collection_name获取描述 | 有（Client.describe(name: str) -> DashVectorResponse） |

### list
*结论：可满足*
mem0 文档说明
```
List all vectors in a collection.

Args:
    filters (Dict, optional): Filters to apply to the list.
    limit (int, optional): Number of vectors to return. Defaults to 100.

Returns:
    List[OutputData]: List of vectors.
```
| mem0 中的要求                       | 阿里云向量                                                                |
|---------------------------------|----------------------------------------------------------------------|
| 根据 collection_name 获取所有的 vector | 有（Collection.query() 参数只使用 filter 和 topk, include_vector=True 就可以实现） |
