from typing import Dict, Any, List
from tortoise import fields, Model

class RelationManager:
    """关系管理器"""
    def __init__(self, model: Model):
        self.model = model
        self._relation_fields: Dict[str, fields.relational.RelationalField] = {
            field_name: field 
            for field_name, field in self.model._meta.fields_map.items()
            if isinstance(field, (
                fields.relational.ForeignKeyFieldInstance,
                fields.relational.OneToOneFieldInstance,
                fields.relational.ManyToManyFieldInstance
            ))
        }

    async def get_fetch_fields(self) -> List[str]:
        """获取需要预加载的字段"""
        return list(self._relation_fields.keys())

    async def process_relations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理关系字段"""
        processed_data = data.copy()
        
        for field_name, field in self._relation_fields.items():
            if field_name not in data:
                continue
                
            field_value = data[field_name]
            
            try:
                if isinstance(field, (fields.relational.ForeignKeyFieldInstance, fields.relational.OneToOneFieldInstance)):
                    # 处理外键和一对一关系
                    if not field_value:
                        processed_data[f"{field_name}_id"] = None
                        del processed_data[field_name]
                        continue
                        
                    if isinstance(field_value, dict):
                        # 如果是字典，创建或获取关联对象
                        related_obj = await field.related_model.get_or_create(**field_value)
                        processed_data[f"{field_name}_id"] = related_obj[0].id
                        del processed_data[field_name]
                    else:
                        # 如果是 ID，验证关联对象是否存在
                        related_id = int(field_value)
                        related_obj = await field.related_model.get_or_none(id=related_id)
                        if not related_obj:
                            raise ValueError(f"关联对象不存在: {field_name} = {related_id}")
                        processed_data[f"{field_name}_id"] = related_id
                        del processed_data[field_name]
                        
                elif isinstance(field, fields.relational.ManyToManyFieldInstance):
                    # 处理多对多关系
                    if not isinstance(field_value, (list, tuple)):
                        raise ValueError(f"多对多关系字段必须是列表: {field_name}")
                        
                    # 验证所有关联对象是否存在
                    related_ids = []
                    for item in field_value:
                        if isinstance(item, dict):
                            # 如果是字典，创建或获取关联对象
                            related_obj = await field.related_model.get_or_create(**item)
                            related_ids.append(related_obj[0].id)
                        else:
                            # 如果是 ID，验证关联对象是否存在
                            related_id = int(item)
                            related_obj = await field.related_model.get_or_none(id=related_id)
                            if not related_obj:
                                raise ValueError(f"关联对象不存在: {field_name} = {related_id}")
                            related_ids.append(related_id)
                            
                    processed_data[field_name] = related_ids
                    
            except Exception as e:
                raise ValueError(f"处理关系字段 {field_name} 时出错: {str(e)}")
                
        return processed_data

    async def setup_relations(self, instance: Model, data: dict) -> None:
        """设置关系"""
        for field_name, field in self._relation_fields.items():
            if field_name not in data:
                continue
                
            try:
                if isinstance(field, fields.relational.ManyToManyFieldInstance):
                    # 处理多对多关系
                    relation_manager = getattr(instance, field_name)
                    await relation_manager.clear()
                    
                    related_ids = data[field_name]
                    if not related_ids:
                        continue
                        
                    # 验证所有关联对象是否存在
                    related_model = field.related_model
                    existing_objects = await related_model.filter(id__in=related_ids)
                    
                    # 添加新的关系
                    await relation_manager.add(*existing_objects)
                    
            except Exception as e:
                raise ValueError(f"设置字段 {field_name} 的关系时出错: {str(e)}") 