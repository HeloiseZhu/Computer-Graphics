void CCGPainterView::ScanlineConvertion(CDC *pDC, MyPolygon ThePolygon, COLORREF fillCol)
{
	//Write your own scan-line convertion algorithm here.
 
	/*定义结构体用于活性边表AET和新边表NET*/
	typedef struct XET
	{
		double x;
		double dx, ymax;
		XET* next;
	}AET,NET;
 
	//CPoint *ThePolygon.m_Vertex;
	int vertNum = ThePolygon.m_VerticeNumber;
 
	/*计算最高点y的坐标,扫描线扫到y的最高点就结束*/
	int MaxY = ThePolygon.m_Vertex[0].y;
	int MinY = ThePolygon.m_Vertex[0].y;
	int i;
	for (i = 1; i < vertNum; i++){
		if (ThePolygon.m_Vertex[i].y>MaxY)
			MaxY = ThePolygon.m_Vertex[i].y;
 
		if (MinY > ThePolygon.m_Vertex[i].y)
			MinY = ThePolygon.m_Vertex[i].y;
	}
	/*初始化AET表，这是一个有头结点的链表*/
	AET *pAET = new AET;
	pAET->next = NULL;
	/*初始化NET表，这也是一个有头结点的链表，头结点的dx，x，ymax都初始化为0*/
	NET *pNET[1024];
	for (i = 0; i <= MaxY; i++){
		pNET[i] = new NET;
		pNET[i]->dx = 0;
		pNET[i]->x = 0;
		pNET[i]->ymax = 0;
		pNET[i]->next = NULL;
	}
 
	/*扫描并建立NET表*/
	for (i = MinY; i <= MaxY; i++){
		/*i表示扫描线，扫描线从多边形的最底端开始，向上扫描*/
		for (int j = 0; j < vertNum;j++)
			/*如果多边形的该顶点与扫描线相交，判断该点为顶点的两条直线是否在扫描线上方
			 *如果在上方，就记录在边表中，并且是头插法记录，结点并没有按照x值进行排序，毕竟在更新AET的时候还要重新排一次
			 *所以NET表可以暂时不排序
			*/
			if (ThePolygon.m_Vertex[j].y == i){
					/*笔画前面的那个点*/
				if (ThePolygon.m_Vertex[(j - 1 + vertNum) % vertNum].y > ThePolygon.m_Vertex[j].y){
						NET *p = new NET;
						p->x = ThePolygon.m_Vertex[j].x;
						p->ymax = ThePolygon.m_Vertex[(j - 1 + vertNum) % vertNum].y;
						p->dx = double((ThePolygon.m_Vertex[(j - 1 + vertNum) % vertNum].x - ThePolygon.m_Vertex[j].x)) / double((ThePolygon.m_Vertex[(j - 1 + vertNum) % vertNum].y - ThePolygon.m_Vertex[j].y));
						p->next = pNET[i]->next;
						pNET[i]->next = p;
					}
					/*笔画后面的那个点*/
				if (ThePolygon.m_Vertex[(j + 1 + vertNum) % vertNum].y > ThePolygon.m_Vertex[j].y){
						NET *p = new NET;
						p->x = ThePolygon.m_Vertex[j].x;
						p->ymax = ThePolygon.m_Vertex[(j + 1 + vertNum) % vertNum].y;
						p->dx = double((ThePolygon.m_Vertex[(j + 1 + vertNum) % vertNum].x - ThePolygon.m_Vertex[j].x)) / double((ThePolygon.m_Vertex[(j + 1 + vertNum) % vertNum].y - ThePolygon.m_Vertex[j].y));
						p->next = pNET[i]->next;
						pNET[i]->next = p;
					}
			}
	}
	
 
	/*建立并更新活性边表AET*/
	for (i = MinY; i <= MaxY; i++){
		/*更新活性边表AET，计算扫描线与边的新的交点x，此时y值没有达到临界值的话*/
		NET *p = pAET->next;
		while (p){
			p->x = p->x + p->dx;
			p = p->next;
		}
		
		/*更新完以后，对活性边表AET按照x值从小到大排序*/
		AET *tq = pAET;
		p = pAET->next;
		tq->next = NULL;
		while (p){
			while (tq->next&&p->x >= tq->next->x)
				tq = tq->next;
			NET *s = p->next;
			p->next = tq->next;
			tq->next = p;
			p = s;
			tq = pAET;
		}
 
		/*从AET表中删除ymax==i的结点*/
		AET *q = pAET;
		p = q->next;
		while (p){
			if (p->ymax == i){
				q->next = p->next;
				delete p;
				p = q->next;
			}
			else{
				q = q->next;
				p = q->next;
			}
		}
		/*将NET中的新点加入AET，并用插入法按X值递增排序*/
		p = pNET[i]->next;
		q = pAET;
		while (p){
			while (q->next&&p->x >= q->next->x)
				q = q->next;
			NET *s = p->next;
			p->next = q->next;
			q->next = p;
			p = s;
			q = pAET;
		}
 
		/*配对填充颜色*/
		p = pAET->next;
		while (p&&p->next){
			for (float j = p->x; j <= p->next->x; j++){
				pDC->SetPixel(static_cast<int>(j), i,fillCol);
			}
			p = p->next->next;
		}
	}
	
}