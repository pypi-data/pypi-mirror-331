import json
from elora.const import supported_models, model_dict
import importlib.resources as pkg_resources

lora_base = "elora.assets"

def rank_pattern(model, base_rank, target_modules="all", layers="all", score=1):
    """
    score = 1
    this will be removed in the future
    values are 1, 2, 3, 4


    layers is optional, default is "all"

    target_module is optional, default is "all"
    E.g. meta-llama/Llama-3.2-1B-Instruct
    target_modules = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ]

    Attention Block (LlamaAttention):
    q_proj
    k_proj
    v_proj
    o_proj
    MLP Block (LlamaMLP):
    gate_proj
    up_proj
    down_proj
    """

    if model not in supported_models:
        raise ValueError(f"model {model} is not supported")

    model_name = model_dict[model]

    if score < 6 :
        methods = [
            "spectral_norm",  # 0
            "frobenius_norm", # 1
            "stable_rank",   # 2
            "nuclear_stable_rank", # 3
            "nuclear_norm", # 4
            "effective_rank", # 5
        ]

        importance_path = f"scores/self/{model_name}/{methods[score]}.json"
    
    elif score < 17:
        methods = [
            "MSE", # 6
            "MAE", # 7
            "Cosine", # 8
            "Angular", # 9
            "Frobenius", # 10
            "SSIM", # 11 
            "Pearson", # 12 
            "KL", # 13 
            "Wasserstein", # 14
            "Jaccard", # 15
            "PSNR", # 16
        ]
        model_name_base = model_name.replace("-it", "")
        importance_path = f"scores/similarity/{model_name_base}/importance_scores_{methods[score-6]}.json"


    
    dims_path = f"dims/{model_name}.json"

    with pkg_resources.files(lora_base).joinpath(importance_path).open() as f:
        importance_factors = json.load(f)

    with pkg_resources.files(lora_base).joinpath(dims_path).open() as f:
        dims = json.load(f)

    if target_modules == "all":
        target_modules = importance_factors.keys()

    num_layers = dims["num_layers"]

    if layers == "all":
        layers = list(range(num_layers))

    num_layers = len(layers)

    # Filter out the target modules
    filtered_importance_factors = {
        key: value for key, value in importance_factors.items() if key in target_modules
    }
    # Filter out the layers
    filtered_importance_factors = {
        key: [value[i] for i in layers if i < len(value)]
        for key, value in filtered_importance_factors.items()
    }

    num_trainable_params_layer = 0
    for i in target_modules:
        num_trainable_params_layer += dims["dims"][i] * base_rank

    num_trainable_params = num_trainable_params_layer * num_layers

    total_importance_sum = 0.0
    for j in layers:
        for i in target_modules:
            total_importance_sum += importance_factors[i][j] * dims["dims"][i]

    alpha = num_trainable_params / total_importance_sum

    ranks = {}
    for j in layers:
        for i in target_modules:
            rank = max(int(round(importance_factors[i][j] * alpha)), 1)
            if i in ["gate_proj", "up_proj", "down_proj"]:
                ranks[f"model.layers.{j}.self_attn.{i}"] = rank
            elif i in ["q_proj", "k_proj", "v_proj", "o_proj"]:
                ranks[f"model.layers.{j}.self_attn.{i}"] = rank
            else:
                raise ValueError(f"module {i} is not supported")

    return ranks


if __name__ == "__main__":
    # for scores in range(17):
    #     ranks = rank_pattern(
    #         model="meta-llama/Llama-3.2-1B-Instruct",
    #         base_rank=16,
    #         target_modules="all",
    #         # target_modules=["q_proj", "down_proj"],
    #         # layers="all",
    #         layers=[2, 3],
    #         score=scores,
    #     )

    #     print(ranks)
    ranks = rank_pattern(
        model="meta-llama/Llama-3.2-1B-Instruct",
        base_rank=16,
        target_modules="all",
        # target_modules=["q_proj", "down_proj"],
        # layers="all",
        layers=[2, 3],
        score=5,
    )

    print(ranks)