from metabolism.StabilityTester import StabilityTester
from metabolism import Helper
import SimpleITK as sitk
import numpy as np
import os,json
from pathlib import Path
import pandas as pd
from scipy import stats, linalg
helper = Helper()

def resample_image(input_image, reference_image,default=0):
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(reference_image)
    
    resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    
    resampler.SetOutputSpacing(reference_image.GetSpacing())
    resampler.SetOutputOrigin(reference_image.GetOrigin())
    resampler.SetOutputDirection(reference_image.GetDirection())
    
    resampler.SetSize(reference_image.GetSize())
    resampler.SetDefaultPixelValue(default)
    return resampler.Execute(input_image)
class StabilityTester:
    def __init__(self):
        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'
    def suvseg2feature(self,dataset,modelname):
        print(f"[{self.INFO_ICON}] Load SUV and SEG from :", dataset)
        infos = pd.read_csv(os.path.join(dataset,"info.csv"))
        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            print("-"*20)
            suv = os.path.join(dataset,file)
            segpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"merge.nii.gz")
            if not os.path.exists(segpath):
                print(f"[{self.ERROR_ICON}] No segment result for Model {modelname}\n    SUV path:{suv}")
                continue
            print(f" [{self.RUNNING_ICON }] Processing: {suv}")
            suv = sitk.ReadImage(suv)
            seg = sitk.ReadImage(segpath)
            suv = resample_image(suv,seg,default=0)
            featpath = f"{Path(segpath).parent}/{modelname}#suvr.json"
            feat = extract_suv_based_roi(suv,seg,modelname=modelname)
            tmp = infos[infos.name == "#".join(file.replace(".nii.gz","").split("#")[1:])]
            gender = tmp.Gender.values[0]
            age = tmp.Age.values[0]
            weight = tmp.Weight.values[0]
            feat.update({'gender':gender,"age":age,"weight":weight})
            with open(featpath,"w") as f:
                json.dump(feat,f)
            print(f" [{self.SUCCESS_ICON}SUCCESS] roi features are written into: {featpath}")
    def analyze(self,dataset,modelname):
        print(f"[{self.INFO_ICON}] Load FEAT from :", dataset)
        feats = []
        for file in os.listdir(dataset):
            if "SUV" not in file or ".nii.gz" not in file:
                continue
            suv = os.path.join(dataset,file)
            segpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),"merge.nii.gz")
            if not os.path.exists(segpath):
                print(f"[{self.ERROR_ICON}] No segment result for Model {modelname}\n    SUV path:{suv}")
                continue
            featpath = os.path.join(dataset,"{}#{}".format(modelname,file.replace(".nii.gz","")),f"{modelname}#suvr.json")
            with open(featpath,"r") as f:
                feat = json.load(f)
            feats.append(feat)
        df = self._preprocess_feature(feats)
        result = detailed_nan_inspection(df)
        if result["msg"] == "error":
            print(f"[{self.ERROR_ICON} WRONG] Feature has NAN or INF")
        else:
            print(f"[{self.SUCCESS_ICON} SUCCESS] Feature has no NAN or INF")
        print('-'*20)
        print(f"[{self.INFO_ICON}] Starting stability Test. Data Count:{len(df)}")
        self.full_refnetwork = self.robust_partial_correlation(df)
        results = {}
        for n in range(10,len(df)+1):
            mean_,std_ = self.bootstrap_pcorr_stability(df,resample_size=n,n_iter=100)
            results[n] = (mean_,std_)
            print(f" [{self.SUCCESS_ICON}] resample size:{n}, correlation coefficient:{mean_}")
        return df,results
    def _preprocess_feature(self,feats):
        processed = []
        for feat in feats:
            try:
                subject_data = {
                    'Age': int(feat['age']),  # 转换字符串年龄为整数
                    'Sex': 0 if feat['gender'] == 'M' else 1,  # 性别编码
                    'Weight': feat['weight']
                }
                for key in feat:
                    if key in ['background', 'gender', 'age', 'weight','L-Substantia nigra','R-Substantia nigra']:
                        continue  #
                    subject_data[key] = feat[key]['meansuvr']
                processed.append(subject_data)
            except:
                pass
        return pd.DataFrame(processed)
    def bootstrap_pcorr_stability(self,df, resample_size, n_iter=20, seed=42):
        np.random.seed(seed)
        covar_cols = ['Age', 'Sex', 'Weight']  # 根据实际情况修改
        all_pcorr_flatten = []
        correlations = []
        for _ in range(n_iter):
            idx = np.random.choice(df.index,size=resample_size,replace=False)
            sub_df = df.loc[idx].copy()
            sub_refnetwork = self.robust_partial_correlation(sub_df)
            
            flat_full = self.full_refnetwork[~np.eye(self.full_refnetwork.shape[0], dtype=bool)]
            flat_sub = sub_refnetwork[~np.eye(sub_refnetwork.shape[0], dtype=bool)]
            r = np.corrcoef(flat_full, flat_sub)[0,1]
            correlations.append(r)
        return np.mean(correlations), np.std(correlations)
    
    def robust_partial_correlation(self,df):
        regions = [col for col in df.columns if col not in ['Age', 'Sex', 'Weight']]
        X = df[regions].values

        covar = np.column_stack([
            df['Age'].values,
            df['Sex'].values,
            np.ones(len(df))  # 截距项
        ])
        
        covar = (covar - covar.mean(axis=0)) / (covar.std(axis=0) + 1e-8)
        residuals = []
        for i in range(X.shape[1]):
            try:
                beta = linalg.lstsq(covar, X[:,i], cond=1e-6)[0]
            except LinAlgError:
                beta = np.dot(np.linalg.pinv(covar), X[:,i])
            resid = X[:,i] - np.dot(covar, beta)
            residuals.append(resid)
        
        residuals = np.array(residuals).T
        residuals += np.random.normal(0, 1e-8, residuals.shape)
        pcorr = np.corrcoef(residuals, rowvar=False)
        np.fill_diagonal(pcorr, 0)
        return pcorr

def extract_suv_based_roi(suv,seg,modelname):
    seg = sitk.GetArrayFromImage(seg)
    suv = sitk.GetArrayFromImage(suv)
    if modelname == "mpum":
        atlasinfo = helper.get_mpum_categories()
        brainzone= [x for x in range(132,215)]
    op = {}
    mask = np.isin(seg, brainzone)
    meanAllBrainSUV = np.mean(suv[mask])
    for i in range(0,len(atlasinfo)):
        tmp = suv[seg == i]
        if len(tmp) == 0:
            continue
        meansuvr = np.mean(tmp) / meanAllBrainSUV
        maxsuvr = np.max(tmp) / meanAllBrainSUV
        op[atlasinfo[str(i)]] = {"meansuvr":float(meansuvr),"maxsuvr":float(maxsuvr)}
    
    return op

def detailed_nan_inspection(df):
    nan_report = df.isna().sum().to_frame('NaN Count')
    inf_report = pd.DataFrame(index=df.columns, columns=['Inf Count'])
    
    # 遍历所有列检测无限值
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            inf_report.loc[col] = np.isinf(df[col]).sum()
        else:
            inf_report.loc[col] = 0  # 非数值列无inf
    
    # 合并报告并筛选问题列
    report = nan_report.join(inf_report)
    problem_cols = report[(report['NaN Count']>0) | (report['Inf Count']>0)]
    
    # 可视化显示
    if not problem_cols.empty:
        display(problem_cols.style.bar(color='#FFA07A'))
        sample_info = {}
        for col in problem_cols.index:
            bad_samples = df[col][df[col].isna() | np.isinf(df[col])].index[:3]  # 显示前3个异常样本
            sample_info[col] = f"异常样本ID: {list(bad_samples)}"
        return {"msg":"error"}
    else:
        return {"msg":"correct"}