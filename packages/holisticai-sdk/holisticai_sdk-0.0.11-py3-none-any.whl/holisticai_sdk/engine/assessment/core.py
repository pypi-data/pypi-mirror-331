from holisticai_sdk.engine.definitions import Dataset, Bootstrapping, BootstrapModelMetrics, LearningTask, Vertical
from holisticai_sdk.engine.models import get_baselines, get_proxy_from_sdk_model
from holisticai_sdk.engine.metrics.efficacy._compute_metrics import efficacy_metrics
from holisticai_sdk.engine.metrics.bias._compute_metrics import bias_metrics
from holisticai_sdk.engine.metrics.explainability._compute_metrics import explainability_metrics
from holisticai_sdk.engine.bootstrap import compute_aggregates_from_bootstrap_metrics
from typing import Literal
from numpy.random import RandomState
from holisticai_sdk.utils.logger import get_logger
from typing import Any

logger = get_logger(__name__)
MAX_SAMPLES = 1000


def get_dataset(task: LearningTask, params: dict, dataset_type: Literal["train", "test"]):
    vertical = params["vertical"]
    match task:
        case "clustering" if vertical == "bias":
            ds = Dataset(learning_task=task, vertical=vertical, X=params[f"X_{dataset_type}"], group_a=params[f"group_a_{dataset_type}"], group_b=params[f"group_b_{dataset_type}"])
        
        case "clustering" if vertical != "bias":
            ds = Dataset(learning_task=task, vertical=vertical, X=params[f"X_{dataset_type}"])

        case _ as task_ if task_!= "clustering" and vertical == "bias":
            ds = Dataset(learning_task=task_, vertical=vertical, X=params[f"X_{dataset_type}"], y_true=params[f"y_{dataset_type}"], group_a=params[f"group_a_{dataset_type}"], group_b=params[f"group_b_{dataset_type}"])

        case _ as task_ if task_!= "clustering" and vertical != "bias":
            ds = Dataset(learning_task=task_, vertical=vertical, X=params[f"X_{dataset_type}"], y_true=params[f"y_{dataset_type}"])

        case _:
            raise NotImplementedError
        
    return ds


def get_baseline_models(task: LearningTask, params: dict):
    logger.info(f"Getting baseline models for task: {task}")
    X_train = params["X_train"]

    if task == "clustering":
        return get_baselines(
            learning_task=task, x=X_train, n_clusters=params["n_clusters"]
        )
    
    y_train = params["y_train"]

    return get_baselines(learning_task=task, x=X_train, y=y_train)
    

def get_proxy(model: Any):
    return get_proxy_from_sdk_model(task=model.task, 
                                    predict_fn=model.predict, 
                                    predict_proba_fn=model.predict_proba,
                                    classes=model.classes,
                                    name=model.name)

def run_assessment(model:Any, params: dict, just_model: bool = False):
    num_bootstraps = params.get("num_bootstraps", 2)    
    random_state = params.get("seed", RandomState(42))

    if isinstance(random_state, int):
        random_state = RandomState(random_state)

    test = get_dataset(model.task, params, dataset_type="test")

    hai_model = get_proxy(model)

    baselines = [hai_model]
    
    if not just_model:
        baselines += get_baseline_models(hai_model.learning_task, params)

    bootstrapping = Bootstrapping(
        num_bootstraps=num_bootstraps,
        max_samples=MAX_SAMPLES,
        random_state=random_state,
        )

    if test.vertical == "bias":
        import functools 
        compute_metrics = functools.partial(bias_metrics, test=test)
    
    elif test.vertical == "efficacy":
        import functools 
        compute_metrics = functools.partial(efficacy_metrics, test=test)

    elif test.vertical == "explainability":
        import functools 
        compute_metrics = functools.partial(explainability_metrics, test=test)
    else:
        raise ValueError(f"Vertical {params['vertical']} not supported")

    boostrap_metrics = []
    for model in baselines:
        logger.info(f"Assessing {model.name}...")
        boostrap_metrics.append(
            BootstrapModelMetrics(model_name=model.name, metrics=compute_metrics(model=model, bootstrapping=bootstrapping))
        )
    logger.info("Assessing complete.")
    metrics = compute_aggregates_from_bootstrap_metrics(boostrap_metrics)
    return dump_metrics(metrics)

def dump_metrics(metrics: list[BootstrapModelMetrics]):
    dumped_results = []
    for model in metrics:
        dumped_result = {
            'method':model['model_name'],   
            'metrics':[metric.model_dump() for metric in model['metrics']]
        }
        dumped_results.append(dumped_result)
    return dumped_results
